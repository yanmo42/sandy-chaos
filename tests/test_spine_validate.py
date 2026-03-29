import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import spine_common, spine_validate


class SpineCommonParsingTests(unittest.TestCase):
    def test_parse_simple_yaml_treats_inline_empty_list_as_empty_list(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.yaml"
            path.write_text(
                "id: SC-CONCEPT-0001\n"
                "tested_by: []\n"
                "depends_on: []\n",
                encoding="utf-8",
            )

            data = spine_common.parse_simple_yaml(path)

            self.assertEqual(data["tested_by"], [])
            self.assertEqual(data["depends_on"], [])


class SpineValidationTests(unittest.TestCase):
    def test_validator_passes_on_current_repo_spine(self):
        result = subprocess.run(
            ["python3", "scripts/spine_validate.py"],
            cwd=spine_common.ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Spine validation passed.", result.stdout)

    def test_validate_concepts_flags_missing_dependency(self):
        item = spine_common.LoadedItem(
            path=Path("spine/concepts/SC-CONCEPT-9999.yaml"),
            data={
                "id": "SC-CONCEPT-9999",
                "name": "broken-concept",
                "summary": "broken",
                "lane": "theory",
                "claim_tier": "plausible",
                "status": "draft",
                "depends_on": ["SC-CONCEPT-0001", "SC-CONCEPT-1234"],
                "documented_in": [],
                "implemented_in": [],
                "tested_by": [],
                "contradicts": [],
                "failure_conditions": ["fails"],
                "next_action": "fix it",
                "promotion_target": "docs/archive",
                "owner_surface": "sandy-chaos",
            },
        )
        errors = []
        warnings = []
        concept_ids = spine_validate.validate_concepts([item], errors, warnings)
        spine_validate.validate_concept_references([item], concept_ids, errors)

        self.assertTrue(any("missing concept 'SC-CONCEPT-0001'" in e or "missing concept 'SC-CONCEPT-1234'" in e for e in errors))

    def test_validate_promotion_events_flags_unknown_concept(self):
        item = spine_common.LoadedItem(
            path=Path("spine/promotions/ledger.jsonl"),
            line=1,
            data={
                "id": "SC-PROMOTE-20260328-99",
                "date": "2026-03-28",
                "concepts": ["SC-CONCEPT-4242"],
                "from_status": "draft",
                "to_status": "canonical",
                "promotion_target": "docs/canonical",
                "basis": "test",
                "disposition": "DOC_PROMOTE",
            },
        )
        errors = []
        warnings = []

        spine_validate.validate_promotion_events([item], {"SC-CONCEPT-0001"}, errors, warnings)

        self.assertTrue(any("missing concept 'SC-CONCEPT-4242'" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
