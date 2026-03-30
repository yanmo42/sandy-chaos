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

    def test_parse_simple_yaml_handles_subsystem_and_membrane_lists(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.yaml"
            path.write_text(
                "source_docs:\n"
                "  - docs/17_endosymbiosis_and_host_assimilation.md\n"
                "between_layers:\n"
                "  - memory\n"
                "  - circulatory\n",
                encoding="utf-8",
            )

            data = spine_common.parse_simple_yaml(path)

            self.assertEqual(data["source_docs"], ["docs/17_endosymbiosis_and_host_assimilation.md"])
            self.assertEqual(data["between_layers"], ["memory", "circulatory"])


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
        self.assertIn("- 2 membranes", result.stdout)
        self.assertIn("- 2 subsystems", result.stdout)

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

    def test_validate_membranes_flags_invalid_layer(self):
        item = spine_common.LoadedItem(
            path=Path("spine/membranes/bad-v1.yaml"),
            data={
                "membrane_id": "bad-membrane-v1",
                "between_layers": ["memory", "mystery"],
                "purpose": "broken",
                "allowed_flows": ["context slices"],
                "forbidden_flows": ["memory-only triggers"],
                "required_evidence": ["artifact path"],
                "authority_limits": ["memory informs only"],
                "artifacts_emitted": ["log record"],
                "failure_mode": "drift",
                "governed_by": ["docs/17_endosymbiosis_and_host_assimilation.md"],
                "notes": "test",
            },
        )
        errors = []
        warnings = []

        spine_validate.validate_membranes([item], errors, warnings)

        self.assertTrue(any("invalid between_layers entry 'mystery'" in e for e in errors))

    def test_validate_subsystems_flags_missing_membrane_and_lane_mismatch(self):
        item = spine_common.LoadedItem(
            path=Path("spine/subsystems/SC-SUBSYSTEM-9999-bad.yaml"),
            data={
                "subsystem_id": "SC-SUBSYSTEM-9999",
                "name": "bad-subsystem",
                "status": "infrastructural",
                "authority_class": "infrastructural",
                "host_layer": "memory",
                "repo_lane": "validation",
                "host_function": "continuity retrieval",
                "purpose": "broken",
                "non_goals": ["none"],
                "inputs": ["memory artifacts"],
                "outputs": ["retrieval paths"],
                "upstream_dependencies": ["memory/*"],
                "downstream_consumers": ["planner"],
                "governed_by": ["validation reports"],
                "claim_classes_supported": ["C", "E"],
                "evidence_classes_produced": ["retrieval evidence"],
                "promotion_relevance": "supports continuity",
                "workflow_participation": "partial",
                "interface_clarity": "medium",
                "evidence_maturity": "mixed",
                "bounded_influence": "explicit",
                "removal_impact": "degrades",
                "failure_if_removed": "memory gets worse",
                "main_risks": ["drift"],
                "membrane_contracts": ["missing-membrane-v1"],
                "source_docs": ["docs/17_endosymbiosis_and_host_assimilation.md"],
                "notes": "test",
            },
        )
        errors = []
        warnings = []

        spine_validate.validate_subsystems([item], {"memory-dispatch-v1"}, errors, warnings)

        self.assertTrue(any("references missing membrane 'missing-membrane-v1'" in e for e in errors))
        self.assertTrue(any("repo_lane 'validation' is inconsistent with host_layer 'memory'" in e for e in errors))

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
