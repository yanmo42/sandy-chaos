"""Proof-frontier state helpers for Sandy Chaos / Ygg.

This module keeps one ranked frontier backlog and one active frontier.
It is deliberately small and file-backed so the proof-governance contract stays
inspectable.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ALLOWED_LEVELS = {1, 2, 3, 4, 5}
ALLOWED_STATUSES = {
    "candidate",
    "active",
    "parked",
    "completed",
    "blocked",
}


@dataclass(frozen=True)
class FrontierCandidate:
    concept_id: str
    title: str
    rank: int
    proof_path_level: int
    target_level: int
    status: str = "candidate"
    rationale: str = ""
    next_move: str = ""
    failure_condition: str = ""
    evidence: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FrontierCandidate":
        return cls(
            concept_id=str(data["concept_id"]).strip(),
            title=str(data["title"]).strip(),
            rank=int(data["rank"]),
            proof_path_level=int(data["proof_path_level"]),
            target_level=int(data["target_level"]),
            status=str(data.get("status", "candidate")).strip(),
            rationale=str(data.get("rationale", "")).strip(),
            next_move=str(data.get("next_move", "")).strip(),
            failure_condition=str(data.get("failure_condition", "")).strip(),
            evidence=_normalize_refs(data.get("evidence", [])),
        )


@dataclass(frozen=True)
class FrontierSnapshot:
    timestamp: str
    active_frontier: str
    frontier_backlog: tuple[FrontierCandidate, ...]
    selection_note: str = ""
    source_artifacts: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "active_frontier": self.active_frontier,
            "selection_note": self.selection_note,
            "source_artifacts": list(self.source_artifacts),
            "frontier_backlog": [candidate.to_dict() for candidate in self.frontier_backlog],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FrontierSnapshot":
        return cls(
            timestamp=str(data["timestamp"]),
            active_frontier=str(data["active_frontier"]).strip(),
            selection_note=str(data.get("selection_note", "")).strip(),
            source_artifacts=_normalize_refs(data.get("source_artifacts", [])),
            frontier_backlog=tuple(
                FrontierCandidate.from_dict(item)
                for item in data.get("frontier_backlog", [])
            ),
        )


def _state_path(root: str | Path) -> Path:
    return Path(root) / "state" / "ygg" / "active-work.json"


def _history_dir(root: str | Path) -> Path:
    return Path(root) / "state" / "ygg" / "frontier-history"


def _normalize_refs(values: Any) -> tuple[str, ...]:
    seen: set[str] = set()
    refs: list[str] = []
    for raw in values or []:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        refs.append(value)
    return tuple(refs)


def _require_text(name: str, value: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def _validate_level(name: str, value: int) -> int:
    level = int(value)
    if level not in ALLOWED_LEVELS:
        raise ValueError(f"{name} must be one of {sorted(ALLOWED_LEVELS)}")
    return level


def _validate_status(value: str) -> str:
    status = str(value).strip()
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"status must be one of {sorted(ALLOWED_STATUSES)}")
    return status


def _normalize_candidates(candidates: list[FrontierCandidate]) -> tuple[FrontierCandidate, ...]:
    if not candidates:
        raise ValueError("frontier_backlog must not be empty")

    seen_ids: set[str] = set()
    normalized: list[FrontierCandidate] = []
    active_count = 0

    sorted_candidates = sorted(candidates, key=lambda item: item.rank)
    expected_ranks = list(range(1, len(sorted_candidates) + 1))
    actual_ranks = [item.rank for item in sorted_candidates]
    if actual_ranks != expected_ranks:
        raise ValueError("frontier_backlog ranks must be contiguous starting at 1")

    for candidate in sorted_candidates:
        concept_id = _require_text("concept_id", candidate.concept_id)
        if concept_id in seen_ids:
            raise ValueError(f"duplicate concept_id in frontier_backlog: {concept_id}")
        seen_ids.add(concept_id)

        status = _validate_status(candidate.status)
        if status == "active":
            active_count += 1

        normalized.append(
            FrontierCandidate(
                concept_id=concept_id,
                title=_require_text("title", candidate.title),
                rank=int(candidate.rank),
                proof_path_level=_validate_level("proof_path_level", candidate.proof_path_level),
                target_level=_validate_level("target_level", candidate.target_level),
                status=status,
                rationale=str(candidate.rationale).strip(),
                next_move=str(candidate.next_move).strip(),
                failure_condition=str(candidate.failure_condition).strip(),
                evidence=_normalize_refs(candidate.evidence),
            )
        )

    if active_count > 1:
        raise ValueError("frontier_backlog may contain only one active candidate")

    return tuple(normalized)


def write_frontier_snapshot(
    root: str | Path,
    *,
    active_frontier: str,
    frontier_backlog: list[FrontierCandidate],
    selection_note: str = "",
    source_artifacts: list[str] | tuple[str, ...] | None = None,
) -> Path:
    active = _require_text("active_frontier", active_frontier)
    normalized = _normalize_candidates(frontier_backlog)
    if normalized[0].concept_id != active:
        raise ValueError("active_frontier must match the rank-1 candidate")

    backlog: list[FrontierCandidate] = []
    for candidate in normalized:
        status = candidate.status
        if candidate.concept_id == active:
            status = "active"
        elif status == "active":
            status = "candidate"
        backlog.append(
            FrontierCandidate(
                concept_id=candidate.concept_id,
                title=candidate.title,
                rank=candidate.rank,
                proof_path_level=candidate.proof_path_level,
                target_level=candidate.target_level,
                status=status,
                rationale=candidate.rationale,
                next_move=candidate.next_move,
                failure_condition=candidate.failure_condition,
                evidence=candidate.evidence,
            )
        )

    snapshot = FrontierSnapshot(
        timestamp=datetime.now(UTC).isoformat(),
        active_frontier=active,
        frontier_backlog=tuple(backlog),
        selection_note=str(selection_note).strip(),
        source_artifacts=_normalize_refs(source_artifacts),
    )

    state_path = _state_path(root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(snapshot.to_dict(), indent=2) + "\n", encoding="utf-8")

    stamp = snapshot.timestamp.replace(":", "-")
    history_path = _history_dir(root) / f"{stamp}_{active}.json"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(snapshot.to_dict(), indent=2) + "\n", encoding="utf-8")
    return state_path


def load_frontier_snapshot(root: str | Path) -> FrontierSnapshot | None:
    path = _state_path(root)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return FrontierSnapshot.from_dict(data)
