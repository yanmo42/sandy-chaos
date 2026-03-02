import tempfile
import unittest
from pathlib import Path

from scripts import self_improve


class SelfImprovePromotionTests(unittest.TestCase):
    def test_classify_policy_tweak_target(self):
        self.assertEqual(
            self_improve.classify_policy_tweak_target("Add validation checklist before commit"),
            self_improve.WORKFLOW_PATH,
        )
        self.assertEqual(
            self_improve.classify_policy_tweak_target("Keep tone concise in group chat"),
            self_improve.AGENTS_PATH,
        )

    def test_append_promoted_tweak_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            doc = Path(td) / "WORKFLOW.md"
            doc.write_text("# Workflow\n", encoding="utf-8")

            changed_first = self_improve.append_promoted_tweak(doc, "Run tests before commit")
            changed_second = self_improve.append_promoted_tweak(doc, "Run tests before commit")

            self.assertTrue(changed_first)
            self.assertFalse(changed_second)
            text = doc.read_text(encoding="utf-8")
            self.assertEqual(text.count("- Run tests before commit"), 1)

    def test_promote_policy_tweaks_updates_docs_and_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            memory = root / "memory"
            memory.mkdir(parents=True, exist_ok=True)

            state_path = memory / "self_improve_state.json"
            state_path.write_text(
                '{\n'
                '  "policy_tweak_counts": {\n'
                '    "Run validation checklist before commit": 3,\n'
                '    "Keep tone concise in group chat": 3\n'
                '  },\n'
                '  "promoted_policy_tweaks": {}\n'
                '}\n',
                encoding="utf-8",
            )

            agents = root / "AGENTS.md"
            workflow = root / "WORKFLOW.md"
            agents.write_text("# Agents\n", encoding="utf-8")
            workflow.write_text("# Workflow\n", encoding="utf-8")

            original = {
                "ROOT": self_improve.ROOT,
                "MEMORY_DIR": self_improve.MEMORY_DIR,
                "STATE_PATH": self_improve.STATE_PATH,
                "AGENTS_PATH": self_improve.AGENTS_PATH,
                "WORKFLOW_PATH": self_improve.WORKFLOW_PATH,
            }
            try:
                self_improve.ROOT = root
                self_improve.MEMORY_DIR = memory
                self_improve.STATE_PATH = state_path
                self_improve.AGENTS_PATH = agents
                self_improve.WORKFLOW_PATH = workflow

                result = self_improve.promote_policy_tweaks(min_count=3, dry_run=False)
                self.assertEqual(len(result["promoted"]), 2)

                state = self_improve.load_state()
                self.assertIn("Run validation checklist before commit", state["promoted_policy_tweaks"])
                self.assertIn("Keep tone concise in group chat", state["promoted_policy_tweaks"])

                self.assertIn("Run validation checklist before commit", workflow.read_text(encoding="utf-8"))
                self.assertIn("Keep tone concise in group chat", agents.read_text(encoding="utf-8"))
            finally:
                self_improve.ROOT = original["ROOT"]
                self_improve.MEMORY_DIR = original["MEMORY_DIR"]
                self_improve.STATE_PATH = original["STATE_PATH"]
                self_improve.AGENTS_PATH = original["AGENTS_PATH"]
                self_improve.WORKFLOW_PATH = original["WORKFLOW_PATH"]


if __name__ == "__main__":
    unittest.main()
