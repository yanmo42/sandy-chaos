import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import automation_activation_gate


class AutomationActivationGateTests(unittest.TestCase):
    def test_build_hourly_command_for_dry_run(self):
        cmd = automation_activation_gate.build_hourly_command(
            stage="dry-run",
            agent="claude",
            dispatch_limit=1,
            agent_timeout_sec=600,
            send_telegram=False,
        )
        joined = " ".join(cmd)
        self.assertIn("hourly_openclaw_cycle.py", joined)
        self.assertIn("--dry-run", joined)
        self.assertNotIn("--allow-push", joined)

    def test_build_hourly_command_for_live(self):
        cmd = automation_activation_gate.build_hourly_command(
            stage="live",
            agent="claude",
            dispatch_limit=1,
            agent_timeout_sec=600,
            send_telegram=True,
        )
        joined = " ".join(cmd)
        self.assertIn("--allow-commit", joined)
        self.assertIn("--allow-push", joined)
        self.assertIn("--send-telegram", joined)

    def test_preflight_marks_dirty_tree_as_blocker_for_live(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            with patch.object(automation_activation_gate, "ROOT", root), \
                 patch.object(automation_activation_gate, "required_binary", return_value=(True, "/usr/bin/mock")), \
                 patch.object(automation_activation_gate, "tracked_worktree_clean", return_value=(False, "tracked working tree is dirty")):
                out = automation_activation_gate.preflight("live", "claude")
        self.assertFalse(out["ok"])
        dirty = next(item for item in out["checks"] if item["name"] == "tracked_worktree_clean")
        self.assertFalse(dirty["ok"])


if __name__ == "__main__":
    unittest.main()
