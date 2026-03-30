"""Minimal scaffolding for Lux–Nyx interaction contract artifacts.

This module defines a small typed record format for early interaction-grammar
work. The intent is to give Sandy Chaos an inspectable surface for recording how
an incoming interaction should be shaped, what transforms are allowed, and what
trace-bearing artifact must remain afterward.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_SCALE = {"low", "medium", "high"}
ALLOWED_EVIDENCE_TIERS = {"defensible", "plausible", "speculative"}
ALLOWED_PRIVACY_LEVELS = {"public", "internal", "sensitive"}
ALLOWED_NYX_OPS = {"gate", "compress", "weight", "tier", "delay", "mask", "trace", "split"}
ALLOWED_SHADOW_ARTIFACTS = {
    "glint",
    "contour",
    "draft",
    "queue-item",
    "promotion-candidate",
    "audit-trace",
    "refusal-artifact",
}


class LuxNyxValidationError(ValueError):
    """Raised when a Lux–Nyx interaction contract record is malformed."""


@dataclass(frozen=True)
class LuxNyxInteractionRecord:
    input_type: str
    input_description: str
    salience: str
    ambiguity: str
    risk: str
    evidence_tier: str
    urgency: str
    privacy_level: str
    allowed_nyx_ops: list[str]
    shadow_artifact_type: str
    shadow_artifact_summary: str
    promotion_condition: str
    failure_condition: str
    trace_requirements: list[str]
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LuxNyxInteractionRecord":
        return cls(
            input_type=data["input_type"],
            input_description=data["input_description"],
            salience=data["salience"],
            ambiguity=data["ambiguity"],
            risk=data["risk"],
            evidence_tier=data["evidence_tier"],
            urgency=data["urgency"],
            privacy_level=data["privacy_level"],
            allowed_nyx_ops=list(data["allowed_nyx_ops"]),
            shadow_artifact_type=data["shadow_artifact_type"],
            shadow_artifact_summary=data["shadow_artifact_summary"],
            promotion_condition=data["promotion_condition"],
            failure_condition=data["failure_condition"],
            trace_requirements=list(data["trace_requirements"]),
            notes=data.get("notes", ""),
        )


def _require_nonempty_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LuxNyxValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _require_enum(value: str, allowed: set[str], field_name: str) -> str:
    cleaned = _require_nonempty_text(value, field_name)
    if cleaned not in allowed:
        raise LuxNyxValidationError(f"{field_name} must be one of {sorted(allowed)}")
    return cleaned


def _require_nonempty_list(values: list[str], field_name: str) -> list[str]:
    if not isinstance(values, list):
        raise LuxNyxValidationError(f"{field_name} must be a list")
    cleaned = [value.strip() for value in values if isinstance(value, str) and value.strip()]
    if not cleaned:
        raise LuxNyxValidationError(f"{field_name} must contain at least one non-empty string")
    return cleaned


def validate_record(record: LuxNyxInteractionRecord) -> None:
    _require_nonempty_text(record.input_type, "input_type")
    _require_nonempty_text(record.input_description, "input_description")
    _require_enum(record.salience, ALLOWED_SCALE, "salience")
    _require_enum(record.ambiguity, ALLOWED_SCALE, "ambiguity")
    _require_enum(record.risk, ALLOWED_SCALE, "risk")
    _require_enum(record.urgency, ALLOWED_SCALE, "urgency")
    _require_enum(record.evidence_tier, ALLOWED_EVIDENCE_TIERS, "evidence_tier")
    _require_enum(record.privacy_level, ALLOWED_PRIVACY_LEVELS, "privacy_level")
    _require_enum(record.shadow_artifact_type, ALLOWED_SHADOW_ARTIFACTS, "shadow_artifact_type")
    _require_nonempty_text(record.shadow_artifact_summary, "shadow_artifact_summary")
    _require_nonempty_text(record.promotion_condition, "promotion_condition")
    _require_nonempty_text(record.failure_condition, "failure_condition")

    allowed_ops = _require_nonempty_list(record.allowed_nyx_ops, "allowed_nyx_ops")
    invalid_ops = [op for op in allowed_ops if op not in ALLOWED_NYX_OPS]
    if invalid_ops:
        raise LuxNyxValidationError(f"allowed_nyx_ops contains invalid entries: {invalid_ops}")

    _require_nonempty_list(record.trace_requirements, "trace_requirements")


def validate_records(records: list[LuxNyxInteractionRecord]) -> None:
    if not isinstance(records, list) or not records:
        raise LuxNyxValidationError("records must be a non-empty list")
    for record in records:
        validate_record(record)


def load_lux_nyx_records(path: str | Path) -> list[LuxNyxInteractionRecord]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, list):
        raise LuxNyxValidationError("Expected a JSON array of Lux–Nyx interaction records")
    records = [LuxNyxInteractionRecord.from_dict(item) for item in data]
    validate_records(records)
    return records
