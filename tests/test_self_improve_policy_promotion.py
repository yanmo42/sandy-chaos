import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


class SelfImprovePromotionTests(unittest.TestCase):
    def _load_module(self):
        root = Path(__file__).resolve().parents[1]
        module_path = root / "scripts" / "self_improve.py"
        spec = importlib.util.spec_from_file_location("self_improve_module", module_path)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        return mod

    def test_promotes_repeated_workflow_tweak_once(self):
        mod = self._load_module()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            memory = tmp / "memory"
            memory.mkdir(parents=True, exist_ok=True)

            mod.MEMORY_DIR = memory
            mod.STATE_PATH = memory / "self_improve_state.json"
            mod.AGENTS_PATH = tmp / "AGENTS.md"
            mod.WORKFLOW_PATH = tmp / "WORKFLOW.md"

            mod.AGENTS_PATH.write_text("# AGENTS\n", encoding="utf-8")
            mod.WORKFLOW_PATH.write_text("# WORKFLOW\n", encoding="utf-8")

            state = mod.default_state()
            tweak = "Run validation before commit in build workflow"
            state["policy_tweak_counts"][tweak] = 3
            mod.save_state(state)

            result = mod.promote_policy_tweaks(min_count=3)
            self.assertEqual(len(result["promoted"]), 1)
            workflow_text = mod.WORKFLOW_PATH.read_text(encoding="utf-8")
            self.assertIn("## Promoted Policy Tweaks", workflow_text)
            self.assertIn(tweak, workflow_text)

            result_again = mod.promote_policy_tweaks(min_count=3)
            self.assertEqual(result_again["promoted"], [])
            workflow_text_again = mod.WORKFLOW_PATH.read_text(encoding="utf-8")
            self.assertEqual(workflow_text_again.count(tweak), 1)

            saved = json.loads(mod.STATE_PATH.read_text(encoding="utf-8"))
            self.assertIn(tweak, saved.get("promoted_policy_tweaks", {}))


if __name__ == "__main__":
    unittest.main()
