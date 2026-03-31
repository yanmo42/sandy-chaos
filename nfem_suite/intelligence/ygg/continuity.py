"""Minimal continuity helpers for the Ygg command surface.

This module keeps the implementation deliberately small:
- checkpoint a branch outcome,
- write a durable cross-session resume artifact,
- load the latest artifact of each type,
- preserve explicit continuity contract fields.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

ALLOWED_DISPOSITIONS = {
    "DROP_LOCAL",
    "LOG_ONLY",
    "TODO_PROMOTE",
    "DOC_PROMOTE",
    "POLICY_PROMOTE",
    "ESCALATE",
}

ALLOWED_PROMOTION_TARGETS = {
    "todo",
    "docs",
    "workflow",
    "foundations",
    "tests/config",
    "log-only",
}

ALLOWED_BRANCH_OUTCOME_CLASSES = {
    "local",
    "promotable",
    "policy-relevant",
    "blocked",
}

ALLOWED_PROMOTION_REVIEW_REQUIREMENTS = {
    "not-required",
    "human-review",
}

ALLOWED_PROMOTION_REVIEW_STATUSES = {
    "not-required",
    "pending",
    "approved",
}


@dataclass(frozen=True)
class ContinuityCheckpoint:
    timestamp: str
    lane: str
    summary: str
    disposition: str
    promotion_target: str = ""
    evidence: str = ""
    next_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContinuityCheckpoint":
        return cls(
            timestamp=data["timestamp"],
            lane=data["lane"],
            summary=data["summary"],
            disposition=data["disposition"],
            promotion_target=data.get("promotion_target", ""),
            evidence=data.get("evidence", ""),
            next_action=data.get("next_action", ""),
        )


@dataclass(frozen=True)
class ContinuityResumeArtifact:
    timestamp: str
    lane: str
    branch_purpose: str
    current_state: str
    branch_outcome_class: str
    disposition: str
    promotion_target: str
    next_action: str
    branch_scope: str = ""
    blocker: str = ""
    summary: str = ""
    evidence: str = ""
    relevant_artifact_refs: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["relevant_artifact_refs"] = list(self.relevant_artifact_refs)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContinuityResumeArtifact":
        return cls(
            timestamp=data["timestamp"],
            lane=data["lane"],
            branch_purpose=data["branch_purpose"],
            current_state=data["current_state"],
            branch_outcome_class=data["branch_outcome_class"],
            disposition=data["disposition"],
            promotion_target=data["promotion_target"],
            next_action=data["next_action"],
            branch_scope=data.get("branch_scope", ""),
            blocker=data.get("blocker", ""),
            summary=data.get("summary", ""),
            evidence=data.get("evidence", ""),
            relevant_artifact_refs=tuple(data.get("relevant_artifact_refs", []) or []),
        )


def _artifact_dir(root: str | Path, artifact_type: str) -> Path:
    if artifact_type == "checkpoint":
        return Path(root) / "state" / "ygg" / "checkpoints"
    if artifact_type == "resume":
        return Path(root) / "state" / "ygg" / "resume"
    raise ValueError(f"Unknown artifact_type: {artifact_type}")


def _require_text(name: str, value: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def _validate_disposition(disposition: str) -> str:
    value = str(disposition).strip()
    if value not in ALLOWED_DISPOSITIONS:
        raise ValueError(f"Invalid disposition: {value}")
    return value


def _validate_promotion_target(promotion_target: str, *, required: bool) -> str:
    value = str(promotion_target).strip()
    if not value:
        if required:
            raise ValueError("promotion_target must be non-empty")
        return ""
    if value not in ALLOWED_PROMOTION_TARGETS:
        raise ValueError(f"Invalid promotion_target: {value}")
    return value


def _validate_branch_outcome_class(branch_outcome_class: str) -> str:
    value = str(branch_outcome_class).strip()
    if value not in ALLOWED_BRANCH_OUTCOME_CLASSES:
        raise ValueError(f"Invalid branch_outcome_class: {value}")
    return value


def _normalize_refs(raw_refs: Iterable[str] | None) -> tuple[str, ...]:
    deduped: list[str] = []
    seen: set[str] = set()
    for raw in raw_refs or []:
        ref = str(raw).strip()
        if not ref or ref in seen:
            continue
        seen.add(ref)
        deduped.append(ref)
    return tuple(deduped)


def _slug_fragment(text: str, *, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:48] or fallback


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_checkpoint(
    root: str | Path,
    *,
    lane: str,
    summary: str,
    disposition: str,
    promotion_target: str = "",
    evidence: str = "",
    next_action: str = "",
) -> Path:
    checkpoint = ContinuityCheckpoint(
        timestamp=datetime.now(UTC).isoformat(),
        lane=_require_text("lane", lane),
        summary=_require_text("summary", summary),
        disposition=_validate_disposition(disposition),
        promotion_target=_validate_promotion_target(promotion_target, required=False),
        evidence=str(evidence).strip(),
        next_action=str(next_action).strip(),
    )

    stamp = checkpoint.timestamp.replace(":", "-")
    lane_slug = _slug_fragment(checkpoint.lane, fallback="lane")
    out_path = _artifact_dir(root, "checkpoint") / f"{stamp}_{lane_slug}.json"
    return _write_json_artifact(out_path, checkpoint.to_dict())


def write_resume_artifact(
    root: str | Path,
    *,
    lane: str,
    branch_purpose: str,
    current_state: str,
    branch_outcome_class: str,
    disposition: str,
    promotion_target: str,
    next_action: str,
    branch_scope: str = "",
    blocker: str = "",
    summary: str = "",
    evidence: str = "",
    relevant_artifact_refs: Iterable[str] | None = None,
) -> Path:
    artifact = ContinuityResumeArtifact(
        timestamp=datetime.now(UTC).isoformat(),
        lane=_require_text("lane", lane),
        branch_purpose=_require_text("branch_purpose", branch_purpose),
        current_state=_require_text("current_state", current_state),
        branch_outcome_class=_validate_branch_outcome_class(branch_outcome_class),
        disposition=_validate_disposition(disposition),
        promotion_target=_validate_promotion_target(promotion_target, required=True),
        next_action=_require_text("next_action", next_action),
        branch_scope=str(branch_scope).strip(),
        blocker=str(blocker).strip(),
        summary=str(summary).strip(),
        evidence=str(evidence).strip(),
        relevant_artifact_refs=_normalize_refs(relevant_artifact_refs),
    )

    stamp = artifact.timestamp.replace(":", "-")
    lane_slug = _slug_fragment(artifact.lane, fallback="lane")
    purpose_slug = _slug_fragment(artifact.branch_purpose, fallback="resume")
    out_path = _artifact_dir(root, "resume") / f"{stamp}_{lane_slug}_{purpose_slug}.json"
    return _write_json_artifact(out_path, artifact.to_dict())


def load_latest_checkpoint(root: str | Path) -> ContinuityCheckpoint | None:
    directory = _artifact_dir(root, "checkpoint")
    if not directory.exists():
        return None
    candidates = sorted(directory.glob("*.json"))
    if not candidates:
        return None
    data = json.loads(candidates[-1].read_text(encoding="utf-8"))
    return ContinuityCheckpoint.from_dict(data)


def load_latest_resume_artifact(root: str | Path) -> ContinuityResumeArtifact | None:
    directory = _artifact_dir(root, "resume")
    if not directory.exists():
        return None
    candidates = sorted(directory.glob("*.json"))
    if not candidates:
        return None
    data = json.loads(candidates[-1].read_text(encoding="utf-8"))
    return ContinuityResumeArtifact.from_dict(data)
