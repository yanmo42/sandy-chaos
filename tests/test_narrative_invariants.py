from nfem_suite.intelligence.narrative_invariants.normalize import normalize_record
from nfem_suite.intelligence.narrative_invariants.symbolic_maps import SymbolicOperatorRecord
from nfem_suite.intelligence.narrative_invariants.validator import ValidationError, validate_record


def make_record(**overrides):
    base = SymbolicOperatorRecord(
        source_object="Gojo Satoru",
        source_domain="Jujutsu Kaisen",
        narrative_role="untouchable elite guardian",
        core_fantasy="inviolable superiority through asymmetry of access",
        signature_operators=["boundary supremacy", "frame-escape"],
        constraint_pattern="extreme power produces distance from peers",
        failure_modes=["detachment"],
        composable_with=["Rimuru Tempest"],
        excluded_domains=["communal softness"],
        confidence_tier="defensible",
        notes="test",
    )
    values = base.__dict__ | overrides
    return SymbolicOperatorRecord(**values)


def test_validate_record_accepts_well_formed_record():
    validate_record(make_record())


def test_validate_record_rejects_bad_confidence_tier():
    record = make_record(confidence_tier="certain")
    try:
        validate_record(record)
    except ValidationError as exc:
        assert "confidence_tier" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_normalize_record_canonicalizes_operator_names():
    record = make_record(signature_operators=[" Frame-Escape ", "boundary supremacy", "boundary supremacy"])
    normalized = normalize_record(record)
    assert normalized.signature_operators == ["boundary supremacy", "frame escape"]
    assert normalized.confidence_tier == "defensible"
