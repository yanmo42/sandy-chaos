"""Lux–Nyx Phase 3: governance coupling — archive/canonical routing.

Connects EvaluatorRecommendation outcomes to concrete governance destinations
and emits inspectable artifacts for every gated, deferred, or refused path.

Public surface:

  route(recommendation, record, root) → GovernanceOutcome
      Maps an evaluator action to a governance destination, enforces the
      evidence gate for promote-candidate, writes a GovernanceArtifact,
      and returns the outcome.

  write_governance_artifact(root, artifact) → Path
      Writes a GovernanceArtifact to state/lux_nyx/governance/.

Governance rule:
  No routing decision is silent.  Every outcome — including surface and
  archive — produces a durable artifact under state/lux_nyx/governance/.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from nfem_suite.intelligence.narrative_invariants.lux_nyx_contract import (
    EvaluatorRecommendation,
    LuxNyxInteractionRecord,
    validate_record,
)
from nfem_suite.intelligence.narrative_invariants.lux_nyx_metrics import (
    record_acceptance,
)

# ---------------------------------------------------------------------------
# Governance destinations
# ---------------------------------------------------------------------------

GOVERNANCE_DESTINATIONS = {
    "surface",         # safe to act on; passed through directly
    "archive",         # preserved but not promoted
    "promotion-queue", # candidate for canonical status; evidence verified
    "hold-queue",      # deferred pending evidence or risk maturity
    "refusal-log",     # rejected; reason recorded as refusal-artifact
    "route-queue",     # needs fast handling by the correct lane
}

# Maps evaluator action → default destination (before evidence gate).
_ACTION_DESTINATION: dict[str, str] = {
    "keep":              "surface",
    "compress":          "surface",
    "route":             "route-queue",
    "archive":           "archive",
    "hold":              "hold-queue",
    "promote-candidate": "promotion-queue",  # may be downgraded by evidence gate
    "refuse-with-reason": "refusal-log",
}

# Evidence gate applied only to promote-candidate.
_EVIDENCE_GATE: dict[str, str] = {
    "defensible":  "promotion-queue",
    "plausible":   "hold-queue",   # not mature enough for canonical promotion
    "speculative": "refusal-log",  # hard gate; no speculative canonical promotion
}


# ---------------------------------------------------------------------------
# GovernanceArtifact
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GovernanceArtifact:
    """Durable record of a governance routing decision.

    Written to state/lux_nyx/governance/ for every route() call.
    """

    timestamp: str
    evaluator_action: str
    destination: str
    evidence_tier: str
    risk: str
    shadow_artifact_type: str
    rationale: str
    trace_note: str

    def to_dict(self) -> dict:
        return asdict(self)


def write_governance_artifact(root: str | Path, artifact: GovernanceArtifact) -> Path:
    """Write a GovernanceArtifact JSON file under state/lux_nyx/governance/."""
    out_dir = Path(root) / "state" / "lux_nyx" / "governance"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = artifact.timestamp.replace(":", "-")
    dest_slug = re.sub(r"[^a-z0-9]+", "-", artifact.destination.lower()).strip("-")
    path = out_dir / f"{stamp}_{dest_slug}.json"
    path.write_text(json.dumps(artifact.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# GovernanceOutcome
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GovernanceOutcome:
    """Result returned by route().

    destination:      where the input was sent
    rationale:        human-readable reason for the routing decision
    trace_note:       audit note combining evaluator and governance reasoning
    artifact_path:    path to the written GovernanceArtifact
    """

    destination: str
    rationale: str
    trace_note: str
    artifact_path: Path


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def route(
    recommendation: EvaluatorRecommendation,
    record: LuxNyxInteractionRecord,
    root: str | Path = Path(__file__).resolve().parents[4],
) -> GovernanceOutcome:
    """Route an EvaluatorRecommendation to a governance destination.

    Steps:
      1. Validate the record (belt-and-suspenders; evaluate() already did this).
      2. Map evaluator action → destination.
      3. For promote-candidate: apply the evidence gate.
      4. Write a GovernanceArtifact.
      5. Return a GovernanceOutcome.

    Evidence gate (promote-candidate only):
      defensible  → promotion-queue   (evidence solid enough)
      plausible   → hold-queue        (needs maturity before canonical)
      speculative → refusal-log       (hard gate; no silent promotion)
    """
    validate_record(record)

    action = recommendation.action
    if action not in _ACTION_DESTINATION:
        raise ValueError(f"Unknown evaluator action: {action!r}")

    destination = _ACTION_DESTINATION[action]
    rationale = recommendation.rationale
    trace_note = recommendation.trace_note

    # Evidence gate — only applies to promote-candidate
    if action == "promote-candidate":
        gated_destination = _EVIDENCE_GATE[record.evidence_tier]
        if gated_destination != destination:
            rationale = (
                f"Governance evidence gate downgraded promote-candidate: "
                f"evidence_tier={record.evidence_tier!r} → {gated_destination}. "
                f"Original evaluator rationale: {rationale}"
            )
            trace_note = (
                f"Evidence gate: evidence_tier={record.evidence_tier} "
                f"redirected to {gated_destination}. {trace_note}"
            )
        destination = gated_destination

    artifact = GovernanceArtifact(
        timestamp=datetime.now(UTC).isoformat(),
        evaluator_action=action,
        destination=destination,
        evidence_tier=record.evidence_tier,
        risk=record.risk,
        shadow_artifact_type=recommendation.shadow_artifact_type,
        rationale=rationale,
        trace_note=trace_note,
    )
    path = write_governance_artifact(root, artifact)

    # Pilot acceptance signal: surface is the only destination where the
    # suggestion is enacted as-is. refusal-log is an explicit rejection.
    # Other destinations (archive, hold-queue, route-queue, promotion-queue)
    # are unresolved at shaping time and neither accept nor reject the
    # suggestion here — promotion-queue in particular is a candidate status,
    # not a measured acceptance.
    if destination == "surface":
        record_acceptance(root, accepted=True)
    elif destination == "refusal-log":
        record_acceptance(root, accepted=False)

    return GovernanceOutcome(
        destination=destination,
        rationale=rationale,
        trace_note=trace_note,
        artifact_path=path,
    )
