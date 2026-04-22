import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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

    def test_run_validation_commands_fails_on_zero_test_discovery(self):
        fake = SimpleNamespace(returncode=0, stdout="Ran 0 tests in 0.000s\n\nOK\n", stderr="")
        with patch("scripts.self_improve.subprocess.run", return_value=fake):
            outcomes = self_improve.run_validation_commands(
                ["./venv/bin/python -m unittest discover -s tests -q"],
                dry_run=False,
            )

        self.assertEqual(len(outcomes), 1)
        self.assertFalse(outcomes[0]["ok"])
        self.assertTrue(outcomes[0]["zero_tests"])
        self.assertEqual(outcomes[0]["ran_tests"], 0)

    def test_run_validation_commands_passes_when_tests_execute(self):
        fake = SimpleNamespace(returncode=0, stdout="Ran 7 tests in 0.012s\n\nOK\n", stderr="")
        with patch("scripts.self_improve.subprocess.run", return_value=fake):
            outcomes = self_improve.run_validation_commands(
                ["./venv/bin/python -m unittest discover -s tests -q"],
                dry_run=False,
            )

        self.assertEqual(len(outcomes), 1)
        self.assertTrue(outcomes[0]["ok"])
        self.assertFalse(outcomes[0]["zero_tests"])
        self.assertEqual(outcomes[0]["ran_tests"], 7)

    def test_compose_fullpass_message_contains_validation_section(self):
        with patch("scripts.self_improve.load_lux_nyx_pilot_snapshot", return_value=None):
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
                    "membrane": {
                        "control_affecting": 2,
                        "descriptive": 1,
                        "continuity_relevant": 2,
                        "memory_consulted": 1,
                        "memory_artifact_refs": 4,
                    },
                    "pipeline": {"orchestrator_ok": False, "autospawn_ok": False},
                    "dispatch": {"attempted": 0, "dispatched": 0, "session_id": "none", "errors": []},
                },
                delta={"done": 0, "partial": 0, "open": 0},
                lane_hits={},
                productive=False,
                productivity_reasons=[],
                validation_outcomes=[{"command": "./venv/bin/python -m unittest -q", "ok": True, "returncode": 0}],
                research_summary={"active": False, "generated": False, "path": None},
            )

        self.assertIn("Validation outcomes (commands run):", msg)
        self.assertIn("PASS (exit 0): `./venv/bin/python -m unittest -q`", msg)
        self.assertIn("dispatch membrane evidence: control-affecting=2, descriptive=1, continuity-relevant=2, memory-consulted=1, artifact-refs=4", msg)
        self.assertIn("Lux–Nyx pilot baseline snapshot:", msg)
        self.assertIn("- unavailable", msg)

    def test_format_lux_nyx_pilot_snapshot_includes_headline_metrics(self):
        text = self_improve.format_lux_nyx_pilot_snapshot(
            {
                "baseline_configured": True,
                "comparison_policy": {
                    "headline_metric_keys": [
                        "suggestion_acceptance_rate",
                        "correction_burden_per_suggestion",
                        "archive_to_promotion_conversion_quality",
                    ]
                },
                "baseline_comparison": {
                    "suggestion_acceptance_rate": {
                        "current": 0.61,
                        "baseline": 0.55,
                        "direction": "better",
                    },
                    "correction_burden_per_suggestion": {
                        "current": 0.19,
                        "baseline": 0.22,
                        "direction": "better",
                    },
                    "archive_to_promotion_conversion_quality": {
                        "current": 0.47,
                        "baseline": 0.4,
                        "direction": "better",
                    },
                },
            }
        )

        self.assertIn("baseline=configured", text)
        self.assertIn("suggestion_acceptance_rate=0.610 vs 0.550 (better)", text)
        self.assertIn("correction_burden_per_suggestion=0.190 vs 0.220 (better)", text)
        self.assertIn("archive_to_promotion_conversion_quality=0.470 vs 0.400 (better)", text)

    def test_default_validation_command_uses_resolved_python(self):
        with patch("scripts.self_improve.resolve_validation_python", return_value="/tmp/python-real"):
            with patch.object(self_improve, "ORCHESTRATOR_CONFIG_PATH", Path("/tmp/missing-orchestrator.json")):
                self.assertEqual(
                    self_improve.resolve_validation_runtime()["commands"],
                    ["/tmp/python-real -m unittest discover -s tests -q"],
                )


if __name__ == "__main__":
    unittest.main()
