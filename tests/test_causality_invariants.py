import json
import tempfile
import unittest
from pathlib import Path

from scripts import self_improve
from scripts.validate_foundations import validate_evidence_payload


def _valid_payload() -> dict:
    return {
        "matrix_id": "T-003",
        "claim_class": "C,E",
        "markers": ["C2", "C3", "A2", "A3"],
        "files_changed": ["scripts/self_improve.py", "scripts/validate_foundations.py"],
        "validation_commands": ["python -m unittest tests.test_causality_invariants -q"],
        "result_summary": "Validator wiring is present and no hard-gate markers are violated.",
        "decision": "PASS",
        "rollback_status": "not needed",
    }


class FoundationsValidatorTests(unittest.TestCase):
    def test_valid_evidence_payload_passes(self):
        result = validate_evidence_payload(_valid_payload())

        self.assertEqual(result["decision"], "PASS")
        self.assertTrue(result["ok"])
        self.assertEqual(result["missing_fields"], [])
        self.assertEqual(result["hard_gate_violations"], [])

    def test_incomplete_payload_reviews_with_clear_missing_fields(self):
        payload = _valid_payload()
        del payload["rollback_status"]
        payload["markers"] = ["C2", "UNKNOWN"]

        result = validate_evidence_payload(payload)

        self.assertEqual(result["decision"], "REVIEW")
        self.assertTrue(result["ok"])
        self.assertIn("rollback_status", result["missing_fields"])
        self.assertIn("UNKNOWN", result["unknown_markers"])
        self.assertIn("missing required fields", result["summary"])

    def test_hard_gate_violation_payload_fails(self):
        payload = _valid_payload()
        payload["markers"] = ["C1", "A2"]
        payload["policy_context"] = {"hard_gate_violations": ["C1"]}

        result = validate_evidence_payload(payload)

        self.assertEqual(result["decision"], "FAIL")
        self.assertFalse(result["ok"])
        self.assertEqual(result["hard_gate_violations"], ["C1"])
        self.assertIn("hard-gate violations: C1", result["summary"])


class SelfImproveFoundationsIntegrationTests(unittest.TestCase):
    def test_run_foundations_validation_returns_review_for_incomplete_payload(self):
        with tempfile.TemporaryDirectory() as td:
            payload_path = Path(td) / "evidence.json"
            payload = _valid_payload()
            del payload["rollback_status"]
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            outcomes = self_improve.run_foundations_validation([str(payload_path)], dry_run=False)

        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["verdict"], "REVIEW")
        self.assertTrue(outcomes[0]["ok"])
        self.assertIn("missing required fields", outcomes[0]["foundations_summary"])

    def test_full_pass_includes_foundations_evidence_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            memory = root / "memory"
            memory.mkdir(parents=True, exist_ok=True)
            outbox = memory / "notification_outbox.md"
            state_path = memory / "self_improve_state.json"
            todo_path = root / "plans" / "todo.md"
            todo_path.parent.mkdir(parents=True, exist_ok=True)
            todo_path.write_text("- [ ] Example task\n", encoding="utf-8")
            payload_path = root / "evidence.json"
            payload_path.write_text(json.dumps(_valid_payload()), encoding="utf-8")

            original = {
                "ROOT": self_improve.ROOT,
                "MEMORY_DIR": self_improve.MEMORY_DIR,
                "STATE_PATH": self_improve.STATE_PATH,
                "NOTIFY_OUTBOX": self_improve.NOTIFY_OUTBOX,
                "TODO_PATH": self_improve.TODO_PATH,
            }
            try:
                self_improve.ROOT = root
                self_improve.MEMORY_DIR = memory
                self_improve.STATE_PATH = state_path
                self_improve.NOTIFY_OUTBOX = outbox
                self_improve.TODO_PATH = todo_path

                ok = self_improve.full_pass(
                    scheduler="heartbeat",
                    send_telegram=False,
                    dry_run=False,
                    max_open_items=3,
                    validation_commands=["python3 -c \"print('Ran 1 test in 0.001s\\n\\nOK')\""],
                    foundations_evidence_paths=[str(payload_path)],
                )
                text = outbox.read_text(encoding="utf-8")
            finally:
                self_improve.ROOT = original["ROOT"]
                self_improve.MEMORY_DIR = original["MEMORY_DIR"]
                self_improve.STATE_PATH = original["STATE_PATH"]
                self_improve.NOTIFY_OUTBOX = original["NOTIFY_OUTBOX"]
                self_improve.TODO_PATH = original["TODO_PATH"]

        self.assertTrue(ok)
        self.assertIn("Validation outcomes (commands run):", text)
        self.assertIn("scripts/validate_foundations.py --payload-file", text)
        self.assertIn("matrix_id=T-003; decision=PASS", text)


if __name__ == "__main__":
    unittest.main()
