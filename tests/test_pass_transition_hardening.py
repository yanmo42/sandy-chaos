"""Tests for PASS-transition comparator-class hardening (AUD-008, AUD-009, Contract 8)."""

import unittest

from scripts.validate_foundations import validate_evidence_payload

_BASE_PAYLOAD = {
    "matrix_id": "T-TEST-001",
    "claim_class": "C",
    "markers": ["O1", "C1"],
    "files_changed": ["scripts/example.py"],
    "validation_commands": ["python3 -m pytest tests/"],
    "result_summary": "All checks passed.",
    "decision": "PASS",
    "rollback_status": "not required",
}


def _pass_payload(**overrides) -> dict:
    p = dict(_BASE_PAYLOAD)
    p.update(overrides)
    return p


class PassTransitionHardeningTests(unittest.TestCase):
    def test_pass_without_comparator_class_is_rejected(self):
        payload = _pass_payload(
            strongest_mundane_comparator="Sagnac effect at measured rotation rate",
            independent_rederivation="Re-derived from first principles; see notebook entry 2026-06-14.",
        )
        result = validate_evidence_payload(payload)
        self.assertNotEqual(result["decision"], "PASS")
        self.assertTrue(
            any("comparator_class" in e for e in result["errors"]),
            msg=f"Expected comparator_class error, got: {result['errors']}",
        )

    def test_pass_without_strongest_mundane_comparator_is_rejected(self):
        payload = _pass_payload(
            comparator_class="Sagnac interferometer baseline",
            independent_rederivation="Re-derived from first principles; see notebook entry 2026-06-14.",
        )
        result = validate_evidence_payload(payload)
        self.assertNotEqual(result["decision"], "PASS")
        self.assertTrue(
            any("strongest_mundane_comparator" in e for e in result["errors"]),
            msg=f"Expected strongest_mundane_comparator error, got: {result['errors']}",
        )

    def test_pass_without_independent_rederivation_is_rejected(self):
        payload = _pass_payload(
            comparator_class="Sagnac interferometer baseline",
            strongest_mundane_comparator="Sagnac effect at measured rotation rate",
        )
        result = validate_evidence_payload(payload)
        self.assertNotEqual(result["decision"], "PASS")
        self.assertTrue(
            any("independent_rederivation" in e for e in result["errors"]),
            msg=f"Expected independent_rederivation error, got: {result['errors']}",
        )

    def test_pass_with_empty_comparator_class_is_rejected(self):
        payload = _pass_payload(
            comparator_class="   ",
            strongest_mundane_comparator="Sagnac effect at measured rotation rate",
            independent_rederivation="Re-derived from first principles; see notebook entry 2026-06-14.",
        )
        result = validate_evidence_payload(payload)
        self.assertNotEqual(result["decision"], "PASS")
        self.assertTrue(
            any("comparator_class" in e for e in result["errors"]),
            msg=f"Expected comparator_class error, got: {result['errors']}",
        )

    def test_pass_with_all_three_fields_is_accepted(self):
        payload = _pass_payload(
            comparator_class="Sagnac interferometer baseline",
            strongest_mundane_comparator="Sagnac effect at measured rotation rate",
            independent_rederivation="Re-derived from first principles; see notebook entry 2026-06-14.",
        )
        result = validate_evidence_payload(payload)
        self.assertEqual(result["decision"], "PASS", msg=f"Unexpected errors: {result['errors']}")

    def test_non_pass_decision_does_not_require_comparator_fields(self):
        payload = {
            "matrix_id": "T-TEST-002",
            "claim_class": "C",
            "markers": ["O1"],
            "files_changed": ["scripts/example.py"],
            "validation_commands": ["python3 -m pytest tests/"],
            "result_summary": "Still in review.",
            "decision": "REVIEW",
            "rollback_status": "not required",
        }
        result = validate_evidence_payload(payload)
        self.assertFalse(
            any("comparator_class" in e for e in result["errors"]),
            msg=f"REVIEW should not require comparator fields, got: {result['errors']}",
        )


if __name__ == "__main__":
    unittest.main()
