"""Lux–Nyx interaction contract artifacts and Phase 1 evaluator.

Phase 0: typed record format — LuxNyxInteractionRecord, validate_record,
         load_lux_nyx_records.

Phase 1: deterministic evaluator — evaluate(record) → EvaluatorRecommendation.
         Rules-based, no ML. Decision logic derived from the four interaction
         regions in docs/archive/lux_nyx_interaction_contract_v0.md.
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


# ---------------------------------------------------------------------------
# Phase 1 — deterministic evaluator
# ---------------------------------------------------------------------------

ALLOWED_EVALUATOR_ACTIONS = {
    "keep",
    "compress",
    "archive",
    "route",
    "hold",
    "promote-candidate",
    "refuse-with-reason",
}


@dataclass(frozen=True)
class EvaluatorRecommendation:
    """Bounded recommendation produced by the Phase 1 evaluator.

    action:               one of ALLOWED_EVALUATOR_ACTIONS
    rationale:            short human-readable reason for the decision
    recommended_nyx_ops:  subset of the record's allowed_nyx_ops to apply
    shadow_artifact_type: carried forward from the record (no override)
    trace_note:           brief note for the trace requirement
    """

    action: str
    rationale: str
    recommended_nyx_ops: tuple[str, ...]
    shadow_artifact_type: str
    trace_note: str


def _select_ops(preferred: list[str], allowed: list[str]) -> tuple[str, ...]:
    """Return preferred ops constrained to allowed, always including trace if available.

    Falls back to all allowed ops if the intersection is empty.
    """
    allowed_set = set(allowed)
    selected = [op for op in preferred if op in allowed_set]
    if "trace" in allowed_set and "trace" not in selected:
        selected.append("trace")
    return tuple(selected) if selected else tuple(allowed)


def evaluate(record: LuxNyxInteractionRecord) -> EvaluatorRecommendation:
    """Apply the Phase 1 rules-based evaluator to a Lux–Nyx interaction record.

    Decision order (first match wins):
      1. High risk + speculative evidence  → refuse-with-reason  (hard gate)
      2. High risk + plausible evidence    → hold                (gate, await maturity)
      3. High risk + defensible evidence   → promote-candidate   (risk acknowledged)
      4. High urgency + low/medium risk    → route               (needs fast handling)
      5. High ambiguity + symbolic/claim   → archive             (preserve, don't over-promote)
      6. High salience + low ambiguity
         + low/medium risk                 → keep                (surface directly)
      7. Default                           → compress            (shape before surfacing)

    The recommended_nyx_ops are always a subset of record.allowed_nyx_ops.
    trace is included whenever it is in allowed_nyx_ops (non-negotiable per contract).
    """
    validate_record(record)
    ops = record.allowed_nyx_ops

    # Rule 1: hard gate — speculative backing is not enough for high-risk action
    if record.risk == "high" and record.evidence_tier == "speculative":
        return EvaluatorRecommendation(
            action="refuse-with-reason",
            rationale=(
                "High risk with only speculative evidence; "
                "gate required before any transform."
            ),
            recommended_nyx_ops=_select_ops(["gate", "trace"], ops),
            shadow_artifact_type=record.shadow_artifact_type,
            trace_note="Refused: risk=high, evidence_tier=speculative.",
        )

    # Rule 2: hold pending evidence maturity
    if record.risk == "high" and record.evidence_tier == "plausible":
        return EvaluatorRecommendation(
            action="hold",
            rationale=(
                "High risk with only plausible evidence; "
                "hold until evidence matures."
            ),
            recommended_nyx_ops=_select_ops(["gate", "weight", "tier", "trace"], ops),
            shadow_artifact_type=record.shadow_artifact_type,
            trace_note="Held: risk=high, evidence_tier=plausible.",
        )

    # Rule 3: promote candidate — risk is high but backing is solid
    if record.risk == "high" and record.evidence_tier == "defensible":
        return EvaluatorRecommendation(
            action="promote-candidate",
            rationale=(
                "High risk but defensible evidence; "
                "promote candidate with audit trace required."
            ),
            recommended_nyx_ops=_select_ops(["gate", "weight", "tier", "trace"], ops),
            shadow_artifact_type=record.shadow_artifact_type,
            trace_note="Promote candidate: risk=high, evidence_tier=defensible.",
        )

    # Rule 4: urgent and safe enough to route immediately
    if record.urgency == "high" and record.risk in {"low", "medium"}:
        return EvaluatorRecommendation(
            action="route",
            rationale="High urgency with acceptable risk; route for immediate handling.",
            recommended_nyx_ops=_select_ops(["compress", "trace"], ops),
            shadow_artifact_type=record.shadow_artifact_type,
            trace_note="Routed: urgency=high.",
        )

    # Rule 5: preserve symbolic/interpretive material without over-promoting
    if record.ambiguity == "high" and record.input_type in {"symbolic-input", "claim"}:
        return EvaluatorRecommendation(
            action="archive",
            rationale=(
                "High ambiguity with symbolic or claim input; "
                "preserve without over-promoting."
            ),
            recommended_nyx_ops=_select_ops(["compress", "tier", "trace"], ops),
            shadow_artifact_type=record.shadow_artifact_type,
            trace_note="Archived: ambiguity=high, input_type symbolic/claim.",
        )

    # Rule 6: clear signal, surface directly
    if (
        record.salience == "high"
        and record.ambiguity == "low"
        and record.risk in {"low", "medium"}
    ):
        return EvaluatorRecommendation(
            action="keep",
            rationale="High salience, low ambiguity, acceptable risk; surface directly.",
            recommended_nyx_ops=_select_ops(["compress", "trace"], ops),
            shadow_artifact_type=record.shadow_artifact_type,
            trace_note="Kept: salience=high, ambiguity=low.",
        )

    # Rule 7: default — shape before surfacing
    return EvaluatorRecommendation(
        action="compress",
        rationale="Default compression path; shape before surfacing.",
        recommended_nyx_ops=_select_ops(["compress", "weight", "trace"], ops),
        shadow_artifact_type=record.shadow_artifact_type,
        trace_note="Compressed: no specific routing condition matched.",
    )
