import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from nfem_suite.intelligence.narrative_invariants.benchmark import (
    InvariantSketchRow,
    SketchValidationError,
    summarize_invariant_sketch,
    validate_invariant_sketch,
)


class SymbolicMapsNormalizationSketchTests(unittest.TestCase):
    def test_validate_rejects_duplicate_artifact_ids(self):
        row = InvariantSketchRow(
            artifact_id="artifact-a",
            artifact_role="role",
            source_mode="mode",
            role_slots=["r1"],
            operator_slots=["o1"],
            constraint_slots=["c1"],
            failure_slots=["f1"],
            boundary_slots=["b1"],
        )
        with self.assertRaises(SketchValidationError):
            validate_invariant_sketch([row, row])

    def test_summarize_reports_full_slot_coverage_for_current_fixture(self):
        root = Path(__file__).resolve().parents[1]
        fixture = root / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"
        rows = json.loads(fixture.read_text(encoding="utf-8"))
        sketch_rows = [InvariantSketchRow.from_dict(item) for item in rows]

        summary = summarize_invariant_sketch(sketch_rows)

        self.assertEqual(summary["artifact_count"], 4)
        self.assertTrue(summary["all_artifacts_fully_populated"])
        self.assertEqual(summary["family_presence"]["role_slots"], 4)
        self.assertEqual(summary["family_presence"]["boundary_slots"], 4)

    def test_script_writes_summary_artifacts(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "symbolic_maps_normalization_sketch_v0.py"
        fixture = root / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"
        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "summary.json"
            out_md = Path(td) / "summary.md"
            result = subprocess.run(
                [
                    "python3",
                    str(script),
                    "--input",
                    str(fixture),
                    "--out-json",
                    str(out_json),
                    "--out-md",
                    str(out_md),
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["all_artifacts_fully_populated"])
            self.assertIn("Symbolic Maps Normalization Sketch v0", out_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
