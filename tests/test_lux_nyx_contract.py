from pathlib import Path

from nfem_suite.intelligence.narrative_invariants.lux_nyx_contract import (
    LuxNyxInteractionRecord,
    LuxNyxValidationError,
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
