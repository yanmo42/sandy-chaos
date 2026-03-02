import unittest

from scripts import self_improve


class FullPassValidationSummaryTests(unittest.TestCase):
    def test_format_validation_outcomes_includes_pass_and_fail(self):
        text = self_improve.format_validation_outcomes(
            [
                {"command": "python -m unittest -q", "ok": True, "returncode": 0},
                {"command": "python -m unittest tests.test_missing", "ok": False, "returncode": 1},
            ]
        )

        self.assertIn("PASS (exit 0): `python -m unittest -q`", text)
        self.assertIn("FAIL (exit 1): `python -m unittest tests.test_missing`", text)

    def test_compose_fullpass_message_contains_validation_section(self):
        msg = self_improve.compose_fullpass_message(
            summary={"created": [], "daily_missed": 0, "weekly_missed": 0},
            todo={"done": 1, "partial": 0, "open": 1, "total": 2, "pct": 50.0},
            open_items=["- [ ] Example task"],
            git_lines=["M scripts/self_improve.py"],
            orch={
                "plan_count": 0,
                "request_count": 0,
                "dispatched_count": 0,
                "latest_run_ids": [],
                "capability_lanes": {},
                "pipeline": {"orchestrator_ok": False, "autospawn_ok": False},
                "dispatch": {"attempted": 0, "dispatched": 0, "session_id": "none", "errors": []},
            },
            delta={"done": 0, "partial": 0, "open": 0},
            lane_hits={},
            productive=False,
            productivity_reasons=[],
            validation_outcomes=[{"command": "./venv/bin/python -m unittest -q", "ok": True, "returncode": 0}],
        )

        self.assertIn("Validation outcomes (commands run):", msg)
        self.assertIn("PASS (exit 0): `./venv/bin/python -m unittest -q`", msg)


if __name__ == "__main__":
    unittest.main()
