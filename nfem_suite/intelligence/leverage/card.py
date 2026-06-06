"""Causal leverage card schema and parser.

The card schema is JSON. Stdlib-only parsing keeps the harness consistent with
the rest of sandy-chaos (see `scripts/spine_common.py`, which avoids PyYAML).

Schema version: leverage-card/v1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

SCHEMA_VERSION = "leverage-card/v1"

ALLOWED_CLAIM_CLASSES = {"F", "C", "E", "S"}
ALLOWED_CLAIM_TIERS = {"defensible", "plausible", "speculative"}
ALLOWED_PRE_REGISTRATION_STATUSES = {"prospective", "retrospective"}
ALLOWED_REVERSIBILITY_CLASSES = {"full", "partial", "none"}
ALLOWED_RISK_LEVELS = {"none", "low", "medium", "high"}
ALLOWED_DECISIONS = {"PASS", "REVIEW", "FAIL"}
ALLOWED_VERIFICATION_METHODS = {
    "deterministic_recomputation",
    "test_suite",
    "stat_significance",
    "human_audit",
    "live_measurement",
    "schema_validation",
}

# Mirrors `scripts/validate_foundations.py` ALLOWED_MARKERS.
ALLOWED_MARKERS = {
    "O1", "O2", "O3",
    "N1", "N2", "N3",
    "I1", "I2", "I3",
    "C1", "C2", "C3", "C4",
    "P1", "P2", "P3",
    "E1", "E2", "E3", "E4", "E5",
    "A1", "A2", "A3",
}
HARD_GATE_MARKERS = {"C1", "I1", "P1", "P2"}

REQUIRED_TOP_LEVEL = (
    "card_id",
    "schema_version",
    "matrix_ref",
    "workflow",
    "claim_class",
    "pre_registration",
    "objective",
    "baseline",
    "intervention",
    "denominators",
    "risk_vector",
    "reversibility",
    "verification",
    "failure_conditions",
    "markers",
    "measured_outcome",
    "decision",
    "provenance",
)

REQUIRED_WORKFLOW = ("name", "surface", "domain")
REQUIRED_OBJECTIVE = ("statement", "metric_name", "metric_definition", "direction")
REQUIRED_BASELINE = ("name", "source")
REQUIRED_INTERVENTION = ("description", "files")
REQUIRED_DENOMINATORS = ("compute", "human_effort", "evidence_cost")
REQUIRED_RISK = (
    "framework_gaming_risk",
    "baseline_cherry_picking_risk",
    "external_action_risk",
    "irreversibility_risk",
)
REQUIRED_REVERSIBILITY = ("class", "rollback_method", "blast_radius")
REQUIRED_VERIFICATION = ("method", "validation_commands", "evidence_artifacts")
REQUIRED_MEASURED = ("summary",)
REQUIRED_DECISION = ("status", "rationale")
REQUIRED_PROVENANCE = ("authored_date", "authored_by")


@dataclass
class LeverageCard:
    """In-memory view of a leverage card. Keeps the raw payload for emission."""

    raw: dict[str, Any]
    source_path: Path | None = None

    # Cached convenience accessors
    card_id: str = ""
    schema_version: str = ""
    matrix_ref: str = ""
    concept_refs: list[str] = field(default_factory=list)
    claim_class: list[str] = field(default_factory=list)
    markers: list[str] = field(default_factory=list)
    pre_registration_status: str = ""
    decision_status: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any], source_path: Path | None = None) -> "LeverageCard":
        if not isinstance(payload, dict):
            raise TypeError("leverage card payload must be a JSON object")
        return cls(
            raw=payload,
            source_path=source_path,
            card_id=str(payload.get("card_id", "")),
            schema_version=str(payload.get("schema_version", "")),
            matrix_ref=str(payload.get("matrix_ref", "")),
            concept_refs=_as_str_list(payload.get("concept_refs")),
            claim_class=_as_str_list(payload.get("claim_class")),
            markers=_as_str_list(payload.get("markers")),
            pre_registration_status=str(
                (payload.get("pre_registration") or {}).get("status", "")
            ),
            decision_status=str(
                (payload.get("decision") or {}).get("status", "")
            ).upper(),
        )


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def load_card(path: str | Path) -> LeverageCard:
    """Load a leverage card from a JSON file on disk."""

    p = Path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    return LeverageCard.from_dict(payload, source_path=p)


def parse_card(payload: dict[str, Any]) -> LeverageCard:
    """Construct a `LeverageCard` from an in-memory dict (no I/O)."""

    return LeverageCard.from_dict(payload)
