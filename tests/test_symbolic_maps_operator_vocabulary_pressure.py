import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class SymbolicMapsOperatorVocabularyPressureTests(unittest.TestCase):
    def test_script_reports_hold_with_one_direct_query_family(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "symbolic_maps_operator_vocabulary_pressure_v0.py"
        fixture = root / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"

        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "operator_pressure.json"
            out_md = Path(td) / "operator_pressure.md"
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
            self.assertEqual(payload["target"], "SC-CONCEPT-0006")
            self.assertEqual(payload["decision"], "hold")
            self.assertEqual(payload["direct_clear_count"], 0)
            self.assertEqual(payload["alias_rescue_families"], ["structural_normalization", "constraint_discipline"])
            self.assertIn("Operator Vocabulary Pressure v0", out_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
