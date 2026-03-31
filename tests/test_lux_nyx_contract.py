from pathlib import Path

from nfem_suite.intelligence.narrative_invariants.lux_nyx_contract import (
    ALLOWED_EVALUATOR_ACTIONS,
    ALLOWED_NYX_OPS,
    EvaluatorRecommendation,
    LuxNyxInteractionRecord,
    LuxNyxValidationError,
    evaluate,
    load_lux_nyx_records,
    validate_record,
)


ROOT = Path(__file__).resolve().parents[1]


def make_record(**overrides):
    base = LuxNyxInteractionRecord(
        input_type="prompt",
        input_description="user asks for the next concrete step on a bounded task",
        salience="high",
        ambiguity="low",
        risk="low",
        evidence_tier="defensible",
        urgency="medium",
        privacy_level="internal",
        allowed_nyx_ops=["compress", "trace"],
        shadow_artifact_type="glint",
        shadow_artifact_summary="ranked next-step suggestion",
        promotion_condition="suggestions consistently help",
        failure_condition="suggestions increase correction burden",
        trace_requirements=["classification", "chosen ops", "output summary"],
        notes="test",
    )
    values = base.__dict__ | overrides
    return LuxNyxInteractionRecord(**values)


def test_validate_record_accepts_well_formed_record():
    validate_record(make_record())


def test_validate_record_rejects_invalid_nyx_op():
    record = make_record(allowed_nyx_ops=["compress", "brood"])
    try:
        validate_record(record)
    except LuxNyxValidationError as exc:
        assert "allowed_nyx_ops" in str(exc)
    else:
        raise AssertionError("expected LuxNyxValidationError")


def test_load_lux_nyx_records_accepts_example_template():
    path = ROOT / "templates" / "lux_nyx_interaction_contract_v0.example.json"
    records = load_lux_nyx_records(path)
    assert len(records) == 3
    assert records[0].shadow_artifact_type == "glint"
    assert "trace" in records[0].allowed_nyx_ops


# ---------------------------------------------------------------------------
# Phase 1 evaluator tests
# ---------------------------------------------------------------------------

def make_full_ops_record(**overrides):
    """Record with all 8 ops allowed, so _select_ops has full range to pick from."""
    base = make_record(
        allowed_nyx_ops=list(ALLOWED_NYX_OPS),
        shadow_artifact_type="audit-trace",
    )
    values = base.__dict__ | overrides
    return LuxNyxInteractionRecord(**values)


def test_evaluate_returns_evaluator_recommendation():
    rec = evaluate(make_record())
    assert isinstance(rec, EvaluatorRecommendation)
    assert rec.action in ALLOWED_EVALUATOR_ACTIONS


def test_evaluate_keeps_high_salience_low_ambiguity_low_risk():
    rec = evaluate(make_record(salience="high", ambiguity="low", risk="low", urgency="medium"))
    assert rec.action == "keep"


def test_evaluate_refuses_high_risk_speculative():
    rec = evaluate(make_full_ops_record(risk="high", evidence_tier="speculative"))
    assert rec.action == "refuse-with-reason"
    assert "speculative" in rec.trace_note


def test_evaluate_holds_high_risk_plausible():
    rec = evaluate(make_full_ops_record(risk="high", evidence_tier="plausible"))
    assert rec.action == "hold"
    assert "plausible" in rec.trace_note


def test_evaluate_promotes_candidate_high_risk_defensible():
    rec = evaluate(make_full_ops_record(risk="high", evidence_tier="defensible"))
    assert rec.action == "promote-candidate"
    assert "defensible" in rec.trace_note


def test_evaluate_routes_high_urgency_low_risk():
    rec = evaluate(make_record(urgency="high", risk="low", salience="medium", ambiguity="medium"))
    assert rec.action == "route"
    assert "urgency=high" in rec.trace_note


def test_evaluate_archives_high_ambiguity_symbolic_input():
    rec = evaluate(make_full_ops_record(
        ambiguity="high",
        input_type="symbolic-input",
        risk="medium",
        urgency="low",
    ))
    assert rec.action == "archive"


def test_evaluate_archives_high_ambiguity_claim():
    rec = evaluate(make_full_ops_record(
        ambiguity="high",
        input_type="claim",
        risk="medium",
        urgency="low",
    ))
    assert rec.action == "archive"


def test_evaluate_compresses_by_default():
    rec = evaluate(make_record(
        salience="low",
        ambiguity="medium",
        risk="low",
        urgency="low",
        input_type="spark",
    ))
    assert rec.action == "compress"


def test_evaluate_recommended_ops_are_subset_of_allowed():
    for _ in range(7):  # hit each rule path
        rec = evaluate(make_full_ops_record(
            risk="high", evidence_tier="speculative",
        ))
        assert all(op in ALLOWED_NYX_OPS for op in rec.recommended_nyx_ops)

    rec = evaluate(make_record())
    allowed_set = set(make_record().allowed_nyx_ops)
    assert all(op in allowed_set for op in rec.recommended_nyx_ops)


def test_evaluate_always_includes_trace_when_allowed():
    # record with trace in allowed_nyx_ops
    rec = evaluate(make_record(allowed_nyx_ops=["compress", "trace"]))
    assert "trace" in rec.recommended_nyx_ops


def test_evaluate_carries_forward_shadow_artifact_type():
    rec = evaluate(make_record(shadow_artifact_type="draft"))
    assert rec.shadow_artifact_type == "draft"


def test_evaluate_high_risk_takes_precedence_over_urgency():
    # urgency=high would normally → route, but risk=high+speculative → refuse first
    rec = evaluate(make_full_ops_record(
        risk="high",
        evidence_tier="speculative",
        urgency="high",
    ))
    assert rec.action == "refuse-with-reason"


def test_evaluate_example_template_records_produce_sensible_actions():
    path = ROOT / "templates" / "lux_nyx_interaction_contract_v0.example.json"
    records = load_lux_nyx_records(path)

    # prompt: high salience, low ambiguity, low risk → keep
    assert evaluate(records[0]).action == "keep"

    # symbolic-input: high ambiguity, symbolic → archive
    assert evaluate(records[1]).action == "archive"

    # claim: high risk, plausible evidence → hold
    assert evaluate(records[2]).action == "hold"
