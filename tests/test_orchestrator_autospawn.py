import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import orchestrator_autospawn


class OrchestratorAutospawnPromptingTests(unittest.TestCase):
    def test_render_contract_prompt_uses_lane_specific_instructions(self):
        prompting = {
            "template": "Lane={lane}\nLaneInstructions:\n{lane_instructions}\nGoal={goal}",
            "globalConstraints": [],
            "byLane": {"sandy-verifier": {"instructions": ["Run adversarial checks"]}},
            "outputContract": [],
            "forbidden": [],
        }
        task = {
            "lane": "sandy-verifier",
            "goal": "Harden frame asymmetry tests",
            "section": "Validation",
            "constraints": ["Stay scoped"],
            "definition_of_done": ["Tests updated"],
            "validation_command": "python -m unittest discover -s tests -q",
        }

        prompt = orchestrator_autospawn.render_contract_prompt(task, prompting=prompting)

        self.assertIn("Lane=sandy-verifier", prompt)
        self.assertIn("Run adversarial checks", prompt)
        self.assertIn("Goal=Harden frame asymmetry tests", prompt)

    def test_to_spawn_request_includes_prompt_context(self):
        task = {
            "lane": "sandy-builder",
            "goal": "Implement minimal config renderer",
            "section": "Ops",
            "constraints": ["Small patch"],
            "definition_of_done": ["Tests pass"],
            "validation_command": "python -m unittest discover -s tests -q",
        }

        req = orchestrator_autospawn.to_spawn_request(task, 1, prompting=orchestrator_autospawn.resolve_prompting_runtime())
        self.assertIn("prompt_context", req)
        self.assertEqual(req["prompt_schema_version"], "v1")
        self.assertTrue(req.get("spawn", {}).get("task", "").strip())

    def test_resolve_prompting_runtime_reads_config(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "orchestrator.json"
            cfg.write_text(
                json.dumps({"prompting": {"template": "Goal={goal}", "globalConstraints": ["A"], "outputContract": [], "forbidden": []}}),
                encoding="utf-8",
            )
            original = orchestrator_autospawn.ORCH_CONFIG
            try:
                orchestrator_autospawn.ORCH_CONFIG = cfg
                runtime = orchestrator_autospawn.resolve_prompting_runtime()
            finally:
                orchestrator_autospawn.ORCH_CONFIG = original

            self.assertEqual(runtime["template"], "Goal={goal}")


class OrchestratorAutospawnDispatchTests(unittest.TestCase):
    def test_build_dispatch_agent_call_uses_configured_agent_id(self):
        req = {"id": "spawn-01", "lane": "sandy-builder", "spawn": {"runtime": "subagent", "task": "x"}}

        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "orchestrator.json"
            cfg.write_text(json.dumps({"dispatch": {"agentId": "sandy-chaos"}}), encoding="utf-8")
            original = orchestrator_autospawn.ORCH_CONFIG
            try:
                orchestrator_autospawn.ORCH_CONFIG = cfg
                payload = orchestrator_autospawn._build_dispatch_agent_call(req)
            finally:
                orchestrator_autospawn.ORCH_CONFIG = original

        self.assertEqual(payload["agentId"], "sandy-chaos")
        self.assertTrue(payload["sessionKey"].startswith("agent:sandy-chaos:orchestrator-"))

    def test_dispatch_uses_agent_gateway_call(self):
        requests = [{"id": "spawn-01", "lane": "sandy-builder", "spawn": {"runtime": "subagent", "task": "x"}}]

        with patch.object(orchestrator_autospawn, "resolve_openclaw_command", return_value=["openclaw"]), \
             patch.object(orchestrator_autospawn, "append_dispatch_log"), \
             patch("scripts.orchestrator_autospawn.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"runId":"r1","status":"accepted"}'
            mock_run.return_value.stderr = ""

            out = orchestrator_autospawn.dispatch_spawn_requests(requests, dry_run=False)

            self.assertEqual(out["attempted"], 1)
            self.assertEqual(out["dispatched"], 1)
            self.assertEqual(len(out["errors"]), 0)

            called = mock_run.call_args[0][0]
            self.assertIn("gateway", called)
            self.assertIn("call", called)
            self.assertIn("agent", called)

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
