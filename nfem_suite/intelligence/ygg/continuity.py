"""Minimal continuity helpers for the Ygg command surface.

This module keeps the first implementation deliberately small:
- checkpoint a branch outcome,
- load the latest checkpoint,
- preserve explicit disposition and promotion target hints.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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


def _checkpoint_dir(root: str | Path) -> Path:
    return Path(root) / "state" / "ygg" / "checkpoints"


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
    if disposition not in ALLOWED_DISPOSITIONS:
        raise ValueError(f"Invalid disposition: {disposition}")
    if promotion_target and promotion_target not in ALLOWED_PROMOTION_TARGETS:
        raise ValueError(f"Invalid promotion_target: {promotion_target}")
    if not lane.strip():
        raise ValueError("lane must be non-empty")
    if not summary.strip():
        raise ValueError("summary must be non-empty")

    checkpoint = ContinuityCheckpoint(
        timestamp=datetime.now(UTC).isoformat(),
        lane=lane.strip(),
        summary=summary.strip(),
        disposition=disposition,
        promotion_target=promotion_target.strip(),
        evidence=evidence.strip(),
        next_action=next_action.strip(),
    )

    out_dir = _checkpoint_dir(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = checkpoint.timestamp.replace(":", "-")
    out_path = out_dir / f"{stamp}_{lane.replace(' ', '_')}.json"
    out_path.write_text(json.dumps(checkpoint.to_dict(), indent=2) + "\n")
    return out_path


def load_latest_checkpoint(root: str | Path) -> ContinuityCheckpoint | None:
    directory = _checkpoint_dir(root)
    if not directory.exists():
        return None
    candidates = sorted(directory.glob("*.json"))
    if not candidates:
        return None
    data = json.loads(candidates[-1].read_text())
    return ContinuityCheckpoint.from_dict(data)
