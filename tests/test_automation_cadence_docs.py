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


if __name__ == "__main__":
    unittest.main()
