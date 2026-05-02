import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from nfem_suite.intelligence.narrative_invariants.lux_nyx_metrics import (
    PilotMetrics,
    build_pilot_report,
    record_acceptance,
    record_correction,
    record_suggestion,
)


class LuxNyxMetricsCliTests(unittest.TestCase):
    def run_cli(self, *args):
        proc = subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(proc.stdout)

    def test_event_report_and_baseline_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            temp_root = Path(td)

            event = self.run_cli(
                "scripts/lux_nyx_pilot_event.py",
                "suggestion",
                "--root",
                str(temp_root),
                "--count",
                "2",
            )
            self.assertEqual(event["status"], "ok")
            self.assertEqual(event["counts"]["suggestion_total"], 2)

            event = self.run_cli(
                "scripts/lux_nyx_pilot_event.py",
                "acceptance",
                "--root",
                str(temp_root),
            )
            self.assertEqual(event["counts"]["suggestion_accepted"], 1)
            self.assertAlmostEqual(event["metrics"]["suggestion_acceptance_rate"], 0.5)

            baseline = self.run_cli(
                "scripts/lux_nyx_pilot_baseline.py",
                "--root",
                str(temp_root),
                "--source",
                "unit-test current proxy",
                "--from-current",
            )
            self.assertTrue(baseline["baseline_configured"])
            self.assertEqual(baseline["baseline_metrics"]["suggestion_acceptance_rate"], 0.5)

            report = self.run_cli(
                "scripts/lux_nyx_pilot_report.py",
                "--root",
                str(temp_root),
                "--summary",
            )
            self.assertEqual(report["status"], "ok")
            self.assertTrue(report["baseline_configured"])
            self.assertTrue((temp_root / "state" / "lux_nyx" / "pilot_report.json").exists())

    def test_baseline_cli_requires_explicit_values_or_current_proxy(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [
                    sys.executable,
                    "scripts/lux_nyx_pilot_baseline.py",
                    "--root",
                    td,
                    "--source",
                    "unit-test",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("baseline values required", proc.stderr)

    def test_acceptance_and_correction_must_consume_unresolved_suggestions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "exceeds unresolved suggestions"):
                record_acceptance(root)

            record_suggestion(root)
            record_acceptance(root)
            with self.assertRaisesRegex(ValueError, "exceeds unresolved suggestions"):
                record_correction(root)

            metrics = PilotMetrics.load(root)
            self.assertEqual(metrics.suggestion_total, 1)
            self.assertEqual(metrics.suggestion_accepted, 1)
            self.assertEqual(metrics.correction_total, 0)

    def test_event_cli_reports_counter_invariant_errors_without_traceback(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [
                    sys.executable,
                    "scripts/lux_nyx_pilot_event.py",
                    "acceptance",
                    "--root",
                    td,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("exceeds unresolved suggestions", proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)

    def test_report_marks_loaded_inconsistent_counters_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            metrics_path = root / "state" / "lux_nyx" / "metrics.json"
            metrics_path.parent.mkdir(parents=True)
            metrics_path.write_text(
                json.dumps({"suggestion_total": 1, "suggestion_accepted": 2}),
                encoding="utf-8",
            )

            report = build_pilot_report(root=root)
            self.assertIn("resolved suggestions cannot exceed suggestion_total", report["invariant_errors"])
            self.assertEqual(report["promotion_verdict"]["verdict"], "invalid-counters")


if __name__ == "__main__":
    unittest.main()
