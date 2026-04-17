import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class SymbolicMapsSchemaHardeningGateTests(unittest.TestCase):
    def test_script_writes_gate_summary_and_reports_single_ready_family(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "symbolic_maps_schema_hardening_gate_v0.py"
        fixture = root / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"

        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "gate.json"
            out_md = Path(td) / "gate.md"
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
            self.assertEqual(payload["hardening_ready_families"], ["failure_slots"])
            self.assertIn("Schema Hardening Gate v0", out_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
