"""Tests for the causal leverage card harness (SC-CONCEPT-0010)."""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nfem_suite.intelligence.leverage import (  # noqa: E402
    LeverageCard,
    evidence_payload,
    load_card,
    score_card,
)
from nfem_suite.intelligence.leverage.card import SCHEMA_VERSION  # noqa: E402
from nfem_suite.intelligence.leverage.scorer import (  # noqa: E402
    ALLOWED_DECISIONS,
    ALLOWED_MARKERS,
)


def _minimal_payload() -> dict:
    """A schema-valid minimal card used as a starting point for negative tests."""

    return {
        "card_id": "LEV-TEST-001",
        "schema_version": SCHEMA_VERSION,
        "matrix_ref": "T-XXX",
        "concept_refs": ["SC-CONCEPT-0010"],
        "workflow": {
            "name": "unit test workflow",
            "surface": "tests/test_leverage_card.py",
            "domain": "validation",
        },
        "claim_class": ["C"],
        "claim_tier": "defensible",
        "pre_registration": {
            "status": "prospective",
            "rationale": "fixture",
            "card_seal_commit": "deadbeef",
        },
        "objective": {
            "statement": "test objective",
            "metric_name": "n_passing_tests",
            "metric_definition": "count of unittest cases that pass",
            "threshold": 1,
            "direction": "greater_is_better",
        },
        "baseline": {
            "name": "zero passing tests",
            "source": "fixture",
        },
        "intervention": {
            "description": "ship the harness",
            "files": ["nfem_suite/intelligence/leverage/"],
        },
        "denominators": {
            "compute": "single python process",
            "human_effort": "single session",
            "evidence_cost": "trivial",
        },
        "risk_vector": {
            "framework_gaming_risk": "low",
            "baseline_cherry_picking_risk": "low",
            "external_action_risk": "none",
            "irreversibility_risk": "none",
        },
        "reversibility": {
            "class": "full",
            "rollback_method": "git revert",
            "blast_radius": "test fixture only",
        },
        "verification": {
            "method": "test_suite",
            "validation_commands": ["python -m unittest tests.test_leverage_card -q"],
            "evidence_artifacts": ["tests/test_leverage_card.py"],
        },
        "failure_conditions": ["no tests pass"],
        "markers": ["C2", "A2"],
        "measured_outcome": {
            "summary": "harness loads and scores fixture",
        },
        "decision": {
            "status": "PASS",
            "rationale": "schema completeness satisfied for fixture",
        },
        "provenance": {
            "authored_date": "2026-06-06",
            "authored_by": "test",
        },
    }


class TestLeverageCardSchema(unittest.TestCase):
    def test_minimal_card_passes(self):
        payload = _minimal_payload()
        card = LeverageCard.from_dict(payload)
        report = score_card(card)
        self.assertEqual(report.decision, "PASS", msg=f"errors={report.errors}")
        self.assertTrue(report.ok)
        self.assertEqual(report.missing_fields, [])
        self.assertEqual(report.unknown_markers, [])
        self.assertEqual(report.hard_gate_violations, [])

    def test_missing_top_level_field_downgrades_to_review(self):
        payload = _minimal_payload()
        del payload["objective"]
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "REVIEW")
        self.assertIn("objective", report.missing_fields)

    def test_missing_nested_required_field_is_caught(self):
        payload = _minimal_payload()
        payload["denominators"].pop("compute")
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "REVIEW")
        self.assertIn("denominators.compute", report.missing_fields)

    def test_unknown_marker_downgrades_to_review(self):
        payload = _minimal_payload()
        payload["markers"] = ["C2", "ZZ9"]
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "REVIEW")
        self.assertIn("ZZ9", report.unknown_markers)

    def test_hard_gate_violation_forces_fail(self):
        payload = _minimal_payload()
        payload["decision"]["violated_markers"] = ["C1"]
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "FAIL")
        self.assertFalse(report.ok)
        self.assertIn("C1", report.hard_gate_violations)

    def test_retrospective_pass_requires_attestation_disclosure(self):
        payload = _minimal_payload()
        payload["pre_registration"]["status"] = "retrospective"
        payload["decision"]["rationale"] = "PASS because effect is large"
        report = score_card(LeverageCard.from_dict(payload))
        self.assertNotEqual(report.decision, "PASS")
        self.assertTrue(any("retrospective" in e.lower() for e in report.errors))

    def test_retrospective_pass_with_attestation_succeeds(self):
        payload = _minimal_payload()
        payload["pre_registration"]["status"] = "retrospective"
        payload["decision"]["rationale"] = (
            "Retrospective attestation; effect size monotonic and large."
        )
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "PASS", msg=f"errors={report.errors}")
        self.assertTrue(any("retrospective" in note for note in report.notes))

    def test_prospective_card_without_seal_emits_warning(self):
        payload = _minimal_payload()
        payload["pre_registration"]["card_seal_commit"] = None
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "PASS")
        self.assertTrue(any("card_seal_commit" in w for w in report.warnings))

    def test_empty_failure_conditions_is_error(self):
        payload = _minimal_payload()
        payload["failure_conditions"] = []
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "REVIEW")
        self.assertTrue(any("failure_conditions" in e for e in report.errors))

    def test_invalid_schema_version_is_error(self):
        payload = _minimal_payload()
        payload["schema_version"] = "leverage-card/v99"
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "REVIEW")
        self.assertTrue(any("schema_version" in e for e in report.errors))

    def test_invalid_risk_level_is_error(self):
        payload = _minimal_payload()
        payload["risk_vector"]["framework_gaming_risk"] = "catastrophic"
        report = score_card(LeverageCard.from_dict(payload))
        self.assertEqual(report.decision, "REVIEW")
        self.assertTrue(any("framework_gaming_risk" in e for e in report.errors))


class TestEvidencePayload(unittest.TestCase):
    def test_evidence_payload_matches_foundations_schema(self):
        from scripts.validate_foundations import REQUIRED_FIELDS, validate_evidence_payload

        payload = _minimal_payload()
        card = LeverageCard.from_dict(payload)
        report = score_card(card)
        evidence = evidence_payload(card, report)

        for field in REQUIRED_FIELDS:
            self.assertIn(field, evidence, msg=f"missing field {field}")

        result = validate_evidence_payload(evidence)
        self.assertNotEqual(result["decision"], "FAIL", msg=result)
        self.assertEqual(result["decision"], "PASS", msg=result)

    def test_evidence_carries_card_id(self):
        payload = _minimal_payload()
        card = LeverageCard.from_dict(payload)
        report = score_card(card)
        evidence = evidence_payload(card, report)
        self.assertEqual(evidence["leverage_card_id"], payload["card_id"])

    def test_marker_set_consistent_with_foundations(self):
        from scripts.validate_foundations import ALLOWED_MARKERS as FOUNDATIONS_MARKERS

        self.assertEqual(ALLOWED_MARKERS, FOUNDATIONS_MARKERS)


class TestCardLoading(unittest.TestCase):
    def test_load_card_round_trip(self):
        payload = _minimal_payload()
        with tempfile.TemporaryDirectory() as tmp:
            card_path = Path(tmp) / "card.json"
            card_path.write_text(json.dumps(payload), encoding="utf-8")
            card = load_card(card_path)
        self.assertEqual(card.card_id, payload["card_id"])
        self.assertEqual(card.matrix_ref, payload["matrix_ref"])
        self.assertEqual(card.markers, payload["markers"])

    def test_load_card_rejects_non_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("not json at all", encoding="utf-8")
            with self.assertRaises(Exception):
                load_card(bad)


class TestRealCardsScoreClean(unittest.TestCase):
    """Sanity-check that every committed card under memory/research/leverage scores."""

    def test_all_committed_cards_score_pass_or_review(self):
        leverage_dir = Path(__file__).resolve().parents[1] / "memory" / "research" / "leverage"
        if not leverage_dir.exists():
            self.skipTest("no leverage cards committed yet")
        cards = sorted(
            p for p in leverage_dir.glob("*.json") if not p.name.endswith(".evidence.json")
        )
        self.assertTrue(cards, "expected at least one committed leverage card")
        for card_path in cards:
            with self.subTest(card=card_path.name):
                card = load_card(card_path)
                report = score_card(card)
                self.assertIn(report.decision, ALLOWED_DECISIONS, msg=report.errors)
                self.assertNotEqual(
                    report.decision,
                    "FAIL",
                    msg=f"{card_path.name}: errors={report.errors}",
                )


if __name__ == "__main__":
    unittest.main()
