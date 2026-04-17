import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class SymbolicMapsOperatorCanonicalizationProbeTests(unittest.TestCase):
    def test_probe_holds_hardening_candidacy_but_below_success_threshold(self):
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "symbolic_maps_operator_canonicalization_probe_v0.py"
        fixture = root / "memory" / "research" / "symbolic-maps-level4" / "normalization_sketch_v0.json"

        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "probe.json"
            out_md = Path(td) / "probe.md"
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
            self.assertEqual(payload["decision"], "hold-hardening-candidacy")
            self.assertLess(payload["direct_pct"], 0.70)
            self.assertEqual(sorted(payload["families_with_shared_multi_artifact"]), ["comparison_reuse", "constraint_discipline", "structural_normalization"])
            self.assertIn("Operator Canonicalization Probe v0", out_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
