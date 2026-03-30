import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_queue_notification_creates_structured_outbox_entry(self):
        with tempfile.TemporaryDirectory() as td:
            outbox = Path(td) / "memory" / "notification_outbox.md"
            original = self_improve.NOTIFY_OUTBOX
            try:
                self_improve.NOTIFY_OUTBOX = outbox
                self_improve.queue_notification("[SANDY-ALERT] hello", dry_run=False)
                self_improve.queue_notification("[SANDY-ALERT] world", dry_run=False)

                text = outbox.read_text(encoding="utf-8")
                day_header = f"## {self_improve.today_str()}"
                self.assertIn("# Notification Outbox", text)
                self.assertEqual(text.count(day_header), 1)
                self.assertIn("[SANDY-ALERT] hello", text)
                self.assertIn("[SANDY-ALERT] world", text)
                self.assertGreaterEqual(text.count("---"), 2)
            finally:
                self_improve.NOTIFY_OUTBOX = original


class SelfImproveDispatchTests(unittest.TestCase):
    def test_dispatch_uses_coordinator_agent_bridge(self):
        with tempfile.TemporaryDirectory() as td:
            req_path = Path(td) / "orchestrator_spawn_requests.json"
            req_path.write_text(
                json.dumps({"requests": [{"id": "spawn-01", "lane": "sandy-builder", "spawn": {"runtime": "subagent", "task": "x"}}]}),
                encoding="utf-8",
            )

            original_req_path = self_improve.ORCH_REQ_PATH
            try:
                self_improve.ORCH_REQ_PATH = req_path
                with patch.object(self_improve, "resolve_openclaw_command", return_value=(["openclaw"], ["openclaw"])), \
                     patch("scripts.self_improve.subprocess.run") as mock_run:
                    mock_run.return_value.returncode = 0
                    mock_run.return_value.stdout = '{"runId":"r1","status":"accepted"}'
                    mock_run.return_value.stderr = ""

                    out = self_improve.dispatch_spawn_requests(dry_run=False, max_dispatch=1)

                self.assertEqual(out["attempted"], 1)
                self.assertEqual(out["dispatched"], 1)
                self.assertEqual(len(out["errors"]), 0)

                called = mock_run.call_args[0][0]
                self.assertIn("gateway", called)
                self.assertIn("call", called)
                self.assertIn("agent", called)
            finally:
                self_improve.ORCH_REQ_PATH = original_req_path

    def test_dispatch_rejects_invalid_continuity_prompt_context(self):
        with tempfile.TemporaryDirectory() as td:
            req_path = Path(td) / "orchestrator_spawn_requests.json"
            req_path.write_text(
                json.dumps(
                    {
                        "requests": [
                            {
                                "id": "spawn-01",
                                "lane": "sandy-builder",
                                "prompt_context": {"goal": "x"},
                                "spawn": {"runtime": "subagent", "task": "x"},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            original_req_path = self_improve.ORCH_REQ_PATH
            try:
                self_improve.ORCH_REQ_PATH = req_path
                with patch.object(self_improve, "resolve_openclaw_command", return_value=(["openclaw"], ["openclaw"])), \
                     patch("scripts.self_improve.subprocess.run") as mock_run:
                    out = self_improve.dispatch_spawn_requests(dry_run=False, max_dispatch=1)

                self.assertEqual(out["attempted"], 1)
                self.assertEqual(out["dispatched"], 0)
                self.assertTrue(any("branch_outcome_class" in e for e in out["errors"]))
                self.assertTrue(any("disposition" in e for e in out["errors"]))
                self.assertTrue(any("promotion_target" in e for e in out["errors"]))
                mock_run.assert_not_called()
            finally:
                self_improve.ORCH_REQ_PATH = original_req_path


class SelfImprovePromptingConfigTests(unittest.TestCase):
    def test_resolve_prompting_runtime_uses_orchestrator_config(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = Path(td) / "orchestrator.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "prompting": {
                            "template": "Goal={goal}",
                            "globalConstraints": ["A"],
                            "byLane": {"sandy-builder": ["Keep scope tight"]},
                            "outputContract": ["Report files"],
                            "forbidden": ["No bypass"],
                        }
                    }
                ),
                encoding="utf-8",
            )

            original = self_improve.ORCHESTRATOR_CONFIG_PATH
            try:
                self_improve.ORCHESTRATOR_CONFIG_PATH = cfg_path
                runtime = self_improve.resolve_prompting_runtime()
            finally:
                self_improve.ORCHESTRATOR_CONFIG_PATH = original

            self.assertEqual(runtime["template"], "Goal={goal}")
            self.assertIn("sandy-builder", runtime["byLane"])

    def test_build_dispatch_payload_renders_from_prompt_context_when_task_missing(self):
        request = {
            "id": "spawn-01",
            "lane": "sandy-builder",
            "spawn": {},
            "prompt_context": {
                "lane": "sandy-builder",
                "section": "Ops",
                "goal": "Improve prompt renderer",
                "constraints": ["Small patch"],
                "definition_of_done": ["Prompt renders"],
                "validation_command": "python -m unittest discover -s tests -q",
            },
        }

        payload = self_improve._build_dispatch_agent_payload(request)
        self.assertIn("Improve prompt renderer", payload["message"])

    def test_build_dispatch_payload_uses_configured_agent_id(self):
        request = {
            "id": "spawn-01",
            "lane": "sandy-builder",
            "spawn": {"task": "Do the thing"},
        }

        with tempfile.TemporaryDirectory() as td:
            cfg_path = Path(td) / "orchestrator.json"
            cfg_path.write_text(json.dumps({"dispatch": {"agentId": "sandy-chaos"}}), encoding="utf-8")

            original = self_improve.ORCHESTRATOR_CONFIG_PATH
            try:
                self_improve.ORCHESTRATOR_CONFIG_PATH = cfg_path
                payload = self_improve._build_dispatch_agent_payload(request)
            finally:
                self_improve.ORCHESTRATOR_CONFIG_PATH = original

        self.assertEqual(payload["agentId"], "sandy-chaos")
        self.assertTrue(payload["sessionKey"].startswith("agent:sandy-chaos:orchestrator-"))


class SelfImproveValidationConfigTests(unittest.TestCase):
    def test_resolve_validation_runtime_uses_orchestrator_config(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = Path(td) / "orchestrator.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "validation": {
                            "commands": {"default": ["python -m unittest discover -s tests -q"]},
                            "policy": {
                                "requireAtLeastOneCommand": True,
                                "requireAllPass": True,
                                "failOnZeroTests": False,
                                "disallowCommandSubstrings": ["|| true"],
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            original = self_improve.ORCHESTRATOR_CONFIG_PATH
            try:
                self_improve.ORCHESTRATOR_CONFIG_PATH = cfg_path
                runtime = self_improve.resolve_validation_runtime()
            finally:
                self_improve.ORCHESTRATOR_CONFIG_PATH = original

            self.assertEqual(runtime["commands"], ["python -m unittest discover -s tests -q"])
            self.assertFalse(runtime["policy"]["failOnZeroTests"])

    def test_run_validation_commands_rejects_disallowed_substrings(self):
        outcomes = self_improve.run_validation_commands(
            ["python -m unittest -q || true"],
            dry_run=False,
            policy={"disallowCommandSubstrings": ["|| true"]},
        )

        self.assertEqual(len(outcomes), 1)
        self.assertFalse(outcomes[0]["ok"])
        self.assertIn("policy_violation", outcomes[0])

    def test_validate_continuity_contract_requires_all_fields(self):
        errors = self_improve.validate_continuity_contract({"goal": "x"})

        self.assertTrue(any("branch_outcome_class" in e for e in errors))
        self.assertTrue(any("disposition" in e for e in errors))
        self.assertTrue(any("promotion_target" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
