"""Minimal benchmark helpers for symbolic-map invariant packets.

This module does not try to prove a universal schema.
It provides one bounded normalization sketch for the current four-artifact
SC-CONCEPT-0006 benchmark so the repeated role/operator/constraint/failure/
boundary skeleton can be checked in code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class InvariantSketchRow:
    artifact_id: str
    artifact_role: str
    source_mode: str
    role_slots: list[str]
    operator_slots: list[str]
    constraint_slots: list[str]
    failure_slots: list[str]
    boundary_slots: list[str]
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InvariantSketchRow":
        return cls(
            artifact_id=str(data["artifact_id"]),
            artifact_role=str(data["artifact_role"]),
            source_mode=str(data["source_mode"]),
            role_slots=list(data["role_slots"]),
            operator_slots=list(data["operator_slots"]),
            constraint_slots=list(data["constraint_slots"]),
            failure_slots=list(data["failure_slots"]),
            boundary_slots=list(data["boundary_slots"]),
            notes=str(data.get("notes", "")),
        )


def load_invariant_sketch(path: str | Path) -> list[InvariantSketchRow]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of invariant sketch rows")
    return [InvariantSketchRow.from_dict(item) for item in data]


class SketchValidationError(ValueError):
    """Raised when the normalization sketch is malformed."""


def _clean_nonempty_strings(values: list[str], field_name: str) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise SketchValidationError(f"{field_name} must contain non-empty strings")
        normalized = " ".join(value.strip().split())
        if normalized not in cleaned:
            cleaned.append(normalized)
    if not cleaned:
        raise SketchValidationError(f"{field_name} must contain at least one item")
    return cleaned


def validate_invariant_sketch(rows: list[InvariantSketchRow]) -> None:
    if not rows:
        raise SketchValidationError("normalization sketch must contain at least one row")

    seen: set[str] = set()
    for row in rows:
        artifact_id = " ".join(row.artifact_id.strip().split())
        if not artifact_id:
            raise SketchValidationError("artifact_id must be non-empty")
        if artifact_id in seen:
            raise SketchValidationError(f"duplicate artifact_id {artifact_id!r}")
        seen.add(artifact_id)

        if not row.artifact_role.strip():
            raise SketchValidationError(f"artifact_role must be non-empty for {artifact_id}")
        if not row.source_mode.strip():
            raise SketchValidationError(f"source_mode must be non-empty for {artifact_id}")

        _clean_nonempty_strings(row.role_slots, "role_slots")
        _clean_nonempty_strings(row.operator_slots, "operator_slots")
        _clean_nonempty_strings(row.constraint_slots, "constraint_slots")
        _clean_nonempty_strings(row.failure_slots, "failure_slots")
        _clean_nonempty_strings(row.boundary_slots, "boundary_slots")


_SLOT_FIELDS = (
    "role_slots",
    "operator_slots",
    "constraint_slots",
    "failure_slots",
    "boundary_slots",
)


def summarize_invariant_sketch(rows: list[InvariantSketchRow]) -> dict[str, Any]:
    validate_invariant_sketch(rows)

    per_artifact: list[dict[str, Any]] = []
    family_presence = {field: 0 for field in _SLOT_FIELDS}
    family_avg_counts = {field: 0.0 for field in _SLOT_FIELDS}

    for row in rows:
        row_counts = {
            "role_slots": len(_clean_nonempty_strings(row.role_slots, "role_slots")),
            "operator_slots": len(_clean_nonempty_strings(row.operator_slots, "operator_slots")),
            "constraint_slots": len(_clean_nonempty_strings(row.constraint_slots, "constraint_slots")),
            "failure_slots": len(_clean_nonempty_strings(row.failure_slots, "failure_slots")),
            "boundary_slots": len(_clean_nonempty_strings(row.boundary_slots, "boundary_slots")),
        }
        for field, count in row_counts.items():
            if count > 0:
                family_presence[field] += 1
            family_avg_counts[field] += count

        per_artifact.append(
            {
                "artifact_id": row.artifact_id,
                "artifact_role": row.artifact_role,
                "source_mode": row.source_mode,
                "slot_counts": row_counts,
                "total_slots": sum(row_counts.values()),
            }
        )

    artifact_count = len(rows)
    for field in family_avg_counts:
        family_avg_counts[field] /= artifact_count

    fully_populated = [
        row["artifact_id"]
        for row in per_artifact
        if all(int(row["slot_counts"][field]) > 0 for field in _SLOT_FIELDS)
    ]

    return {
        "artifact_count": artifact_count,
        "slot_families": list(_SLOT_FIELDS),
        "family_presence": family_presence,
        "family_avg_counts": family_avg_counts,
        "fully_populated_artifacts": fully_populated,
        "all_artifacts_fully_populated": len(fully_populated) == artifact_count,
        "per_artifact": per_artifact,
        "bounds": [
            "This sketch only claims the current four benchmark artifacts can be represented with one repeated slot family.",
            "It does not ratify a global symbolic-maps schema or prove future corpus generalization.",
            "If later artifacts require repeated ad hoc fields, this sketch should be revised or rejected rather than expanded cosmetically.",
        ],
    }
