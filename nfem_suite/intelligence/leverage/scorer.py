"""Causal leverage card scorer.

`score_card` performs schema validation against the card v1 grammar and returns
a `ScoreReport`. `evidence_payload` converts a scored card into a payload that
`scripts/validate_foundations.py` accepts as-is, so each card is one
matrix-row-evidence increment.

The scorer is pure: it does not execute the card's `validation_commands` or
write files. Seal-timestamp verification is dependency-injected via the
`git_show_committer_iso` parameter so the schema check stays I/O-free and
testable; side-effecting helpers live in `scripts/run_leverage_card.py`.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .card import (
    ALLOWED_CLAIM_CLASSES,
    ALLOWED_CLAIM_TIERS,
    ALLOWED_DECISIONS,
    ALLOWED_MARKERS,
    ALLOWED_PRE_REGISTRATION_STATUSES,
    ALLOWED_REVERSIBILITY_CLASSES,
    ALLOWED_RISK_LEVELS,
    ALLOWED_VERIFICATION_METHODS,
    HARD_GATE_MARKERS,
    LeverageCard,
    REQUIRED_BASELINE,
    REQUIRED_DECISION,
    REQUIRED_DENOMINATORS,
    REQUIRED_INTERVENTION,
    REQUIRED_MEASURED,
    REQUIRED_OBJECTIVE,
    REQUIRED_PROVENANCE,
    REQUIRED_REVERSIBILITY,
    REQUIRED_RISK,
    REQUIRED_TOP_LEVEL,
    REQUIRED_VERIFICATION,
    REQUIRED_WORKFLOW,
    SCHEMA_VERSION,
)


@dataclass
class ScoreReport:
    card_id: str
    decision: str  # PASS | REVIEW | FAIL
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    unknown_markers: list[str] = field(default_factory=list)
    hard_gate_violations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    seal_verification: str = "skipped"  # skipped | passed | failed | unverifiable

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "decision": self.decision,
            "ok": self.ok,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "missing_fields": list(self.missing_fields),
            "unknown_markers": list(self.unknown_markers),
            "hard_gate_violations": list(self.hard_gate_violations),
            "notes": list(self.notes),
            "seal_verification": self.seal_verification,
        }


def git_show_committer_iso(sha: str, cwd: str | Path | None = None) -> str | None:
    """Return the committer ISO 8601 timestamp for `sha`, or None on any failure.

    Pure helper that wraps `git show -s --format=%cI`. Used as the default
    `git_show_committer_iso` argument to `score_card` from `run_leverage_card.py`.
    Unit tests inject mocks instead of calling git directly.
    """

    try:
        result = subprocess.run(
            ["git", "show", "-s", "--format=%cI", sha],
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    out = result.stdout.strip()
    return out or None


def score_card(
    card: LeverageCard,
    *,
    git_lookup: Callable[[str], str | None] | None = None,
) -> ScoreReport:
    """Validate the card schema and resolve a final decision."""

    payload = card.raw
    errors: list[str] = []
    warnings: list[str] = []
    missing_fields: list[str] = []
    notes: list[str] = []

    # 0. Schema version handshake.
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"unsupported schema_version: expected {SCHEMA_VERSION!r}, "
            f"got {payload.get('schema_version')!r}"
        )

    # 1. Required top-level fields.
    for field_name in REQUIRED_TOP_LEVEL:
        if payload.get(field_name) in (None, "", [], {}):
            missing_fields.append(field_name)

    # 2. Nested required fields.
    _require_nested(payload, "workflow", REQUIRED_WORKFLOW, missing_fields)
    _require_nested(payload, "objective", REQUIRED_OBJECTIVE, missing_fields)
    _require_nested(payload, "baseline", REQUIRED_BASELINE, missing_fields)
    _require_nested(payload, "intervention", REQUIRED_INTERVENTION, missing_fields)
    _require_nested(payload, "denominators", REQUIRED_DENOMINATORS, missing_fields)
    _require_nested(payload, "risk_vector", REQUIRED_RISK, missing_fields)
    _require_nested(payload, "reversibility", REQUIRED_REVERSIBILITY, missing_fields)
    _require_nested(payload, "verification", REQUIRED_VERIFICATION, missing_fields)
    _require_nested(payload, "measured_outcome", REQUIRED_MEASURED, missing_fields)
    _require_nested(payload, "decision", REQUIRED_DECISION, missing_fields)
    _require_nested(payload, "provenance", REQUIRED_PROVENANCE, missing_fields)

    # 3. Enum constraints.
    pre_reg = (payload.get("pre_registration") or {}).get("status")
    if pre_reg is not None and pre_reg not in ALLOWED_PRE_REGISTRATION_STATUSES:
        errors.append(f"invalid pre_registration.status: {pre_reg!r}")

    for claim in card.claim_class:
        if claim not in ALLOWED_CLAIM_CLASSES:
            errors.append(f"invalid claim_class entry: {claim!r}")

    tier = payload.get("claim_tier")
    if tier is not None and tier not in ALLOWED_CLAIM_TIERS:
        errors.append(f"invalid claim_tier: {tier!r}")

    reversibility_class = (payload.get("reversibility") or {}).get("class")
    if reversibility_class is not None and reversibility_class not in ALLOWED_REVERSIBILITY_CLASSES:
        errors.append(f"invalid reversibility.class: {reversibility_class!r}")

    risk = payload.get("risk_vector") or {}
    for risk_key in REQUIRED_RISK:
        value = risk.get(risk_key)
        if value is not None and value not in ALLOWED_RISK_LEVELS:
            errors.append(f"invalid risk_vector.{risk_key}: {value!r}")

    verification_method = (payload.get("verification") or {}).get("method")
    if verification_method is not None and verification_method not in ALLOWED_VERIFICATION_METHODS:
        errors.append(f"invalid verification.method: {verification_method!r}")

    declared_decision = card.decision_status
    if declared_decision and declared_decision not in ALLOWED_DECISIONS:
        errors.append(f"invalid decision.status: {declared_decision!r}")

    # 4. Markers.
    unknown_markers = [m for m in card.markers if m not in ALLOWED_MARKERS]
    hard_gate_violations = sorted(
        set(_as_str_list((payload.get("decision") or {}).get("violated_markers"))) & HARD_GATE_MARKERS
    )

    # 5. Threshold sanity.
    objective = payload.get("objective") or {}
    threshold = objective.get("threshold")
    if threshold is not None and not isinstance(threshold, (int, float)):
        errors.append(f"objective.threshold must be numeric or null, got {type(threshold).__name__}")
    direction = objective.get("direction")
    if direction is not None and direction not in {"greater_is_better", "lesser_is_better", "neutral"}:
        errors.append(f"invalid objective.direction: {direction!r}")

    # 6. Verification commands non-empty.
    verification_cmds = (payload.get("verification") or {}).get("validation_commands") or []
    if not verification_cmds:
        errors.append("verification.validation_commands must be non-empty")

    # 7. Failure conditions non-empty.
    failure_conditions = payload.get("failure_conditions") or []
    if not failure_conditions:
        errors.append("failure_conditions must be non-empty")

    # 8. Retrospective discipline: PASS+retrospective must disclose attestation.
    if (
        declared_decision == "PASS"
        and pre_reg == "retrospective"
    ):
        rationale = ((payload.get("decision") or {}).get("rationale") or "").lower()
        tokens = ("retrospective", "attestation", "not independent", "not an independent")
        if not any(token in rationale for token in tokens):
            errors.append(
                "retrospective PASS card must declare attestation/non-independent status in decision.rationale"
            )

    # 9. Prospective discipline: seal must exist and (when verifiable) predate measurement.
    seal_verification = "skipped"
    if pre_reg == "prospective":
        pre_reg_block = payload.get("pre_registration") or {}
        seal = pre_reg_block.get("card_seal_commit")
        measurement_ts = pre_reg_block.get("measurement_timestamp")
        if not seal:
            warnings.append(
                "prospective card lacks pre_registration.card_seal_commit; "
                "post-measurement edits will not be auditable"
            )
        elif not measurement_ts:
            warnings.append(
                "prospective card has card_seal_commit but no pre_registration.measurement_timestamp; "
                "seal cannot be verified against measurement time"
            )
            seal_verification = "unverifiable"
        elif git_lookup is None:
            # Caller did not provide a git lookup; pure schema mode.
            seal_verification = "skipped"
        else:
            seal_iso = git_lookup(seal)
            if seal_iso is None:
                warnings.append(
                    f"could not resolve card_seal_commit {seal!r} via git; "
                    "seal-timestamp verification skipped"
                )
                seal_verification = "unverifiable"
            else:
                try:
                    seal_dt = datetime.fromisoformat(seal_iso)
                    measurement_dt = datetime.fromisoformat(measurement_ts)
                except ValueError as exc:
                    errors.append(f"invalid ISO 8601 timestamp during seal verification: {exc}")
                    seal_verification = "failed"
                else:
                    if seal_dt > measurement_dt:
                        errors.append(
                            f"seal_after_measurement: card_seal_commit {seal} committed at "
                            f"{seal_iso} is AFTER pre_registration.measurement_timestamp "
                            f"{measurement_ts} — pre-registration is invalid"
                        )
                        seal_verification = "failed"
                    else:
                        delta = (measurement_dt - seal_dt).total_seconds()
                        notes.append(
                            f"seal_verified: commit {seal} predates measurement_timestamp by {delta:.0f}s"
                        )
                        seal_verification = "passed"

    # 10. Decision resolution.
    if hard_gate_violations or seal_verification == "failed":
        final_decision = "FAIL"
    elif missing_fields or unknown_markers or errors:
        final_decision = "REVIEW"
    elif declared_decision in ALLOWED_DECISIONS:
        final_decision = declared_decision
    else:
        final_decision = "REVIEW"

    if final_decision == "PASS" and pre_reg == "retrospective":
        notes.append("retrospective attestation, not independent re-validation")

    if missing_fields:
        errors.insert(0, "missing required fields: " + ", ".join(sorted(set(missing_fields))))
    if unknown_markers:
        errors.append("unknown markers: " + ", ".join(unknown_markers))

    return ScoreReport(
        card_id=card.card_id,
        decision=final_decision,
        ok=final_decision != "FAIL",
        errors=errors,
        warnings=warnings,
        missing_fields=sorted(set(missing_fields)),
        unknown_markers=unknown_markers,
        hard_gate_violations=hard_gate_violations,
        notes=notes,
        seal_verification=seal_verification,
    )


def evidence_payload(card: LeverageCard, report: ScoreReport) -> dict[str, Any]:
    """Emit a `validate_foundations.py`-compatible evidence payload."""

    payload = card.raw
    intervention = payload.get("intervention") or {}
    verification = payload.get("verification") or {}
    measured = payload.get("measured_outcome") or {}
    reversibility = payload.get("reversibility") or {}

    return {
        "matrix_id": card.matrix_ref or payload.get("matrix_ref", ""),
        "claim_class": ",".join(card.claim_class) if card.claim_class else "",
        "markers": list(card.markers),
        "files_changed": list(intervention.get("files") or []),
        "validation_commands": list(verification.get("validation_commands") or []),
        "result_summary": measured.get("summary") or "",
        "decision": report.decision,
        "rollback_status": (
            f"{reversibility.get('class', 'unknown')}: "
            f"{reversibility.get('rollback_method', 'unspecified')}"
        ),
        "leverage_card_id": card.card_id,
        "leverage_card_pre_registration": (
            (payload.get("pre_registration") or {}).get("status", "")
        ),
        "leverage_card_notes": list(report.notes),
        "leverage_card_seal_verification": report.seal_verification,
    }


def _require_nested(
    payload: dict[str, Any],
    parent_key: str,
    required: tuple[str, ...],
    missing: list[str],
) -> None:
    block = payload.get(parent_key)
    if not isinstance(block, dict):
        return
    for field_name in required:
        value = block.get(field_name)
        if value in (None, "", [], {}):
            missing.append(f"{parent_key}.{field_name}")


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]
