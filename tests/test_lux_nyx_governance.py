"""Tests for lux_nyx_governance.py — Phase 3 governance coupling."""

import json
import tempfile
from pathlib import Path

from nfem_suite.intelligence.narrative_invariants.lux_nyx_contract import (
    EvaluatorRecommendation,
    LuxNyxInteractionRecord,
    evaluate,
)
from nfem_suite.intelligence.narrative_invariants.lux_nyx_governance import (
    GOVERNANCE_DESTINATIONS,
    GovernanceArtifact,
    GovernanceOutcome,
    route,
    write_governance_artifact,
)
from nfem_suite.intelligence.narrative_invariants.lux_nyx_metrics import (
    PilotMetrics,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_record(**overrides) -> LuxNyxInteractionRecord:
    base = LuxNyxInteractionRecord(
        input_type="prompt",
        input_description="run the next action for the sprint",
        salience="high",
        ambiguity="low",
        risk="low",
        evidence_tier="defensible",
        urgency="medium",
        privacy_level="internal",
        allowed_nyx_ops=["compress", "trace"],
        shadow_artifact_type="glint",
        shadow_artifact_summary="shaped next-action",
        promotion_condition="consistently helpful",
        failure_condition="increases correction burden",
        trace_requirements=["classification", "chosen ops", "output summary"],
    )
    values = base.__dict__ | overrides
    return LuxNyxInteractionRecord(**values)


def make_full_ops_record(**overrides) -> LuxNyxInteractionRecord:
    from nfem_suite.intelligence.narrative_invariants.lux_nyx_contract import ALLOWED_NYX_OPS
    base = make_record(allowed_nyx_ops=list(ALLOWED_NYX_OPS), shadow_artifact_type="audit-trace")
    values = base.__dict__ | overrides
    return LuxNyxInteractionRecord(**values)


def make_recommendation(action: str, **overrides) -> EvaluatorRecommendation:
    base = dict(
        action=action,
        rationale="test rationale",
        recommended_nyx_ops=("compress", "trace"),
        shadow_artifact_type="glint",
        trace_note=f"trace: action={action}",
    )
    base.update(overrides)
    return EvaluatorRecommendation(**base)


# ---------------------------------------------------------------------------
# GovernanceArtifact
# ---------------------------------------------------------------------------

def test_governance_artifact_is_frozen():
    artifact = GovernanceArtifact(
        timestamp="2026-04-01T00:00:00+00:00",
        evaluator_action="keep",
        destination="surface",
        evidence_tier="defensible",
        risk="low",
        shadow_artifact_type="glint",
        rationale="High salience.",
        trace_note="Kept.",
    )
    try:
        artifact.destination = "archive"  # type: ignore[misc]
        raise AssertionError("expected FrozenInstanceError")
    except Exception as exc:
        assert "frozen" in str(exc).lower() or "FrozenInstanceError" in type(exc).__name__


def test_governance_artifact_to_dict_serialisable():
    artifact = GovernanceArtifact(
        timestamp="2026-04-01T00:00:00+00:00",
        evaluator_action="keep",
        destination="surface",
        evidence_tier="defensible",
        risk="low",
        shadow_artifact_type="glint",
        rationale="High salience.",
        trace_note="Kept.",
    )
    d = artifact.to_dict()
    json.dumps(d)  # must not raise


# ---------------------------------------------------------------------------
# write_governance_artifact
# ---------------------------------------------------------------------------

def test_write_governance_artifact_creates_file():
    with tempfile.TemporaryDirectory() as td:
        artifact = GovernanceArtifact(
            timestamp="2026-04-01T00:00:00+00:00",
            evaluator_action="archive",
            destination="archive",
            evidence_tier="plausible",
            risk="medium",
            shadow_artifact_type="contour",
            rationale="High ambiguity.",
            trace_note="Archived.",
        )
        path = write_governance_artifact(td, artifact)
        assert path.exists()
        assert path.suffix == ".json"
        data = json.loads(path.read_text())
        assert data["destination"] == "archive"
        assert data["evaluator_action"] == "archive"


def test_write_governance_artifact_path_under_governance_dir():
    with tempfile.TemporaryDirectory() as td:
        artifact = GovernanceArtifact(
            timestamp="2026-04-01T00:00:00+00:00",
            evaluator_action="keep",
            destination="surface",
            evidence_tier="defensible",
            risk="low",
            shadow_artifact_type="glint",
            rationale=".",
            trace_note=".",
        )
        path = write_governance_artifact(td, artifact)
        assert path.parent == Path(td) / "state" / "lux_nyx" / "governance"


def test_write_governance_artifact_filename_includes_destination_slug():
    with tempfile.TemporaryDirectory() as td:
        artifact = GovernanceArtifact(
            timestamp="2026-04-01T00:00:00+00:00",
            evaluator_action="hold",
            destination="hold-queue",
            evidence_tier="plausible",
            risk="high",
            shadow_artifact_type="audit-trace",
            rationale=".",
            trace_note=".",
        )
        path = write_governance_artifact(td, artifact)
        assert "hold-queue" in path.name


# ---------------------------------------------------------------------------
# route — destination mapping
# ---------------------------------------------------------------------------

def test_route_keep_goes_to_surface():
    with tempfile.TemporaryDirectory() as td:
        rec = make_record(salience="high", ambiguity="low", risk="low")
        reco = evaluate(rec)
        assert reco.action == "keep"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "surface"


def test_route_compress_goes_to_surface():
    with tempfile.TemporaryDirectory() as td:
        rec = make_record(salience="low", ambiguity="medium", risk="low", urgency="low", input_type="spark")
        reco = evaluate(rec)
        assert reco.action == "compress"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "surface"


def test_route_archive_goes_to_archive():
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(ambiguity="high", input_type="symbolic-input", risk="medium", urgency="low")
        reco = evaluate(rec)
        assert reco.action == "archive"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "archive"


def test_route_hold_goes_to_hold_queue():
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="plausible")
        reco = evaluate(rec)
        assert reco.action == "hold"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "hold-queue"


def test_route_refuse_goes_to_refusal_log():
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="speculative")
        reco = evaluate(rec)
        assert reco.action == "refuse-with-reason"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "refusal-log"


def test_route_route_action_goes_to_route_queue():
    with tempfile.TemporaryDirectory() as td:
        rec = make_record(urgency="high", risk="low", salience="medium", ambiguity="medium")
        reco = evaluate(rec)
        assert reco.action == "route"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "route-queue"


# ---------------------------------------------------------------------------
# route — evidence gate on promote-candidate
# ---------------------------------------------------------------------------

def test_route_promote_candidate_defensible_goes_to_promotion_queue():
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="defensible")
        reco = evaluate(rec)
        assert reco.action == "promote-candidate"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "promotion-queue"


def test_route_promote_candidate_plausible_downgraded_to_hold_queue():
    """Evidence gate: plausible evidence is not mature enough for canonical promotion."""
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="plausible")
        # Manually construct a promote-candidate recommendation to test the gate
        # independently of evaluator ordering (evaluator returns hold for this combo).
        reco = make_recommendation("promote-candidate")
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "hold-queue"
        assert "evidence gate" in outcome.rationale.lower()


def test_route_promote_candidate_speculative_goes_to_refusal_log():
    """Evidence gate: speculative evidence is a hard gate — no silent promotion."""
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="speculative")
        reco = make_recommendation("promote-candidate")
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "refusal-log"
        assert "evidence gate" in outcome.rationale.lower()


# ---------------------------------------------------------------------------
# route — artifact output
# ---------------------------------------------------------------------------

def test_route_writes_governance_artifact():
    with tempfile.TemporaryDirectory() as td:
        rec = make_record()
        reco = evaluate(rec)
        outcome = route(reco, rec, root=td)
        assert outcome.artifact_path.exists()


def test_route_artifact_is_valid_json_with_required_fields():
    with tempfile.TemporaryDirectory() as td:
        rec = make_record()
        reco = evaluate(rec)
        outcome = route(reco, rec, root=td)
        data = json.loads(outcome.artifact_path.read_text())
        for field in ("evaluator_action", "destination", "evidence_tier", "risk", "rationale", "trace_note"):
            assert field in data, f"missing field: {field}"


def test_route_artifact_under_governance_dir():
    with tempfile.TemporaryDirectory() as td:
        rec = make_record()
        reco = evaluate(rec)
        outcome = route(reco, rec, root=td)
        assert outcome.artifact_path.parent == Path(td) / "state" / "lux_nyx" / "governance"


def test_route_outcome_destination_in_governance_destinations():
    with tempfile.TemporaryDirectory() as td:
        for risk, evidence, urgency in [
            ("low", "defensible", "medium"),
            ("high", "speculative", "low"),
            ("high", "plausible", "low"),
            ("high", "defensible", "low"),
            ("low", "defensible", "high"),
        ]:
            rec = make_full_ops_record(risk=risk, evidence_tier=evidence, urgency=urgency)
            reco = evaluate(rec)
            outcome = route(reco, rec, root=td)
            assert outcome.destination in GOVERNANCE_DESTINATIONS, (
                f"unexpected destination {outcome.destination!r} for "
                f"risk={risk} evidence={evidence} urgency={urgency}"
            )


def test_route_returns_governance_outcome():
    with tempfile.TemporaryDirectory() as td:
        rec = make_record()
        reco = evaluate(rec)
        outcome = route(reco, rec, root=td)
        assert isinstance(outcome, GovernanceOutcome)


# ---------------------------------------------------------------------------
# route — pilot acceptance signal
# ---------------------------------------------------------------------------

def test_route_surface_records_accepted_suggestion():
    """Surfacing a suggestion counts as acceptance for the pilot metric."""
    with tempfile.TemporaryDirectory() as td:
        rec = make_record(salience="high", ambiguity="low", risk="low")
        reco = evaluate(rec)
        assert reco.action == "keep"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "surface"
        metrics = PilotMetrics.load(td)
        assert metrics.suggestion_accepted == 1


def test_route_refusal_log_does_not_record_accepted_suggestion():
    """Refusal is an explicit non-acceptance — suggestion_accepted stays 0."""
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="speculative")
        reco = evaluate(rec)
        assert reco.action == "refuse-with-reason"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "refusal-log"
        metrics = PilotMetrics.load(td)
        assert metrics.suggestion_accepted == 0


def test_route_hold_queue_does_not_record_acceptance():
    """hold-queue is unresolved — neither accepted nor refused at shaping time."""
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="plausible")
        reco = make_recommendation("promote-candidate")
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "hold-queue"
        metrics = PilotMetrics.load(td)
        assert metrics.suggestion_accepted == 0


def test_route_promotion_queue_does_not_record_archive_promotion():
    """promotion-queue is a candidate status, not an archive→promotion conversion.

    Archive-to-promotion tracking requires identity across sessions and must
    be driven by an explicit ``record_archive_to_promotion`` call, not by
    the route() side effect.
    """
    with tempfile.TemporaryDirectory() as td:
        rec = make_full_ops_record(risk="high", evidence_tier="defensible")
        reco = evaluate(rec)
        assert reco.action == "promote-candidate"
        outcome = route(reco, rec, root=td)
        assert outcome.destination == "promotion-queue"
        metrics = PilotMetrics.load(td)
        assert metrics.archive_promoted == 0
