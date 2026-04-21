import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AutomationCadenceDocsTests(unittest.TestCase):
    def test_agentic_automation_loop_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/07_agentic_automation_loop.md").read_text(encoding="utf-8")

        self.assertIn("**fast = edge** cadence", text)
        self.assertIn("**meso = bridge** cadence", text)
        self.assertIn("**slow = spine** cadence", text)
        self.assertIn("should not imply direct fast-to-spine promotion", text)

    def test_research_automation_protocol_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/09_research_automation_protocol.md").read_text(encoding="utf-8")

        self.assertIn("**edge / fast** layer", text)
        self.assertIn("**bridge / meso** layer", text)
        self.assertIn("**spine / slow** layer", text)
        self.assertIn("should not imply raw fast-loop output directly rewriting spine surfaces", text)

    def test_git_automation_protocol_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/08_git_automation_protocol.md").read_text(encoding="utf-8")

        self.assertIn("**edge / fast** layer", text)
        self.assertIn("**bridge / meso** layer", text)
        self.assertIn("**spine / slow** layer", text)
        self.assertIn("should not imply raw edge activity directly rewriting spine policy", text)

    def test_research_ingestion_protocol_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/research_ingestion_protocol.md").read_text(encoding="utf-8")

        self.assertIn("**edge / fast** layer", text)
        self.assertIn("**bridge / meso** layer", text)
        self.assertIn("**spine / slow** layer", text)
        self.assertIn("should not imply raw fast-loop output directly rewriting spine surfaces", text)

    def test_cognitive_tempo_orchestration_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/14_cognitive_tempo_orchestration.md").read_text(encoding="utf-8")

        self.assertIn("**fast = edge** cadence", text)
        self.assertIn("**meso = bridge** cadence", text)
        self.assertIn("**slow = spine** cadence", text)
        self.assertIn(
            "should not imply direct fast-to-spine promotion or any retrocausal rewrite",
            text,
        )

    def test_glossary_temporal_band_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/glossary.md").read_text(encoding="utf-8")

        self.assertIn("**fast = edge** cadence", text)
        self.assertIn("**meso = bridge** cadence", text)
        self.assertIn("**slow = spine** cadence", text)
        self.assertIn(
            "raw fast-band activity should not directly rewrite slow-band state",
            text,
        )

    def test_temporal_predictive_processing_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/16_temporal_predictive_processing.md").read_text(encoding="utf-8")

        self.assertIn("**fast = edge** cadence", text)
        self.assertIn("**meso = bridge** cadence", text)
        self.assertIn("**slow = spine** cadence", text)
        self.assertIn(
            "should not imply direct fast-to-spine promotion or any retrocausal rewrite",
            text,
        )

    def test_yggdrasil_continuity_architecture_makes_edge_bridge_spine_mapping_explicit(self):
        text = (ROOT / "docs/12_yggdrasil_continuity_architecture.md").read_text(encoding="utf-8")

        self.assertIn("**Fast = edge** cadence.", text)
        self.assertIn("**Meso = bridge** cadence.", text)
        self.assertIn("**Slow = spine** cadence.", text)
        self.assertIn("**fast = edge** → sensing, local adaptation, and reversible branch work", text)
        self.assertIn("**meso = bridge** → routing, summarization, comparison, and promotion gating", text)
        self.assertIn("**slow = spine** → consolidation, policy shaping, and long-horizon continuity", text)
        self.assertIn("should not imply direct fast-to-spine promotion", text)
        self.assertIn("retrocausal influence", text)


if __name__ == "__main__":
    unittest.main()
