import unittest
from unittest.mock import patch

from scripts import orchestrator_autospawn


class OrchestratorAutospawnDispatchTests(unittest.TestCase):
    def test_dispatch_uses_sessions_spawn_gateway_call(self):
        requests = [{"id": "spawn-01", "spawn": {"runtime": "subagent", "task": "x"}}]

        with patch.object(orchestrator_autospawn, "resolve_openclaw_command", return_value=["openclaw"]), \
             patch.object(orchestrator_autospawn, "append_dispatch_log"), \
             patch("scripts.orchestrator_autospawn.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"ok":true}'
            mock_run.return_value.stderr = ""

            out = orchestrator_autospawn.dispatch_spawn_requests(requests, dry_run=False)

            self.assertEqual(out["attempted"], 1)
            self.assertEqual(out["dispatched"], 1)
            self.assertEqual(len(out["errors"]), 0)

            called = mock_run.call_args[0][0]
            self.assertIn("gateway", called)
            self.assertIn("call", called)
            self.assertIn("sessions_spawn", called)

    def test_dispatch_dry_run_marks_dispatched_without_subprocess(self):
        requests = [{"id": "spawn-01", "spawn": {"runtime": "subagent", "task": "x"}}]

        with patch.object(orchestrator_autospawn, "resolve_openclaw_command", return_value=["openclaw"]), \
             patch.object(orchestrator_autospawn, "append_dispatch_log"), \
             patch("scripts.orchestrator_autospawn.subprocess.run") as mock_run:
            out = orchestrator_autospawn.dispatch_spawn_requests(requests, dry_run=True)

            self.assertEqual(out["attempted"], 1)
            self.assertEqual(out["dispatched"], 1)
            self.assertEqual(len(out["errors"]), 0)
            mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
