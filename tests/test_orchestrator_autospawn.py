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
            "capability_lane": "continuity",
            "branch_outcome_class": "policy-relevant",
            "disposition": "POLICY_PROMOTE",
            "promotion_target": "tests/config",
            "memory_artifact_ids": ["memory/research/topological-memory-v0/comparison_summary_v0.json"],
            "goal": "Implement minimal config renderer",
            "section": "Ops",
            "constraints": ["Small patch"],
            "definition_of_done": ["Tests pass"],
            "validation_command": "python -m unittest discover -s tests -q",
        }

        req = orchestrator_autospawn.to_spawn_request(task, 1, prompting=orchestrator_autospawn.resolve_prompting_runtime())
        self.assertIn("prompt_context", req)
        self.assertEqual(req["prompt_schema_version"], "v1")
        self.assertEqual(req["prompt_context"].get("capability_lane"), "continuity")
        self.assertEqual(
            req["prompt_context"].get("memory_artifact_ids"),
            ["memory/research/topological-memory-v0/comparison_summary_v0.json"],
        )
        self.assertEqual(req["prompt_context"].get("disposition"), "POLICY_PROMOTE")
        self.assertEqual(req["prompt_context"].get("promotion_target"), "tests/config")
        self.assertEqual(req["prompt_context"].get("branch_outcome_class"), "policy-relevant")
        self.assertTrue(req.get("spawn", {}).get("task", "").strip())
        self.assertIn("Continuity contract:", req["spawn"]["task"])
        self.assertIn("Branch outcome class: policy-relevant", req["spawn"]["task"])
        self.assertIn("Disposition: POLICY_PROMOTE", req["spawn"]["task"])
        self.assertIn("Promotion target: tests/config", req["spawn"]["task"])
        self.assertIn("Continuity evidence artifacts:", req["spawn"]["task"])

    def test_validate_continuity_contract_requires_disposition_and_target(self):
        errors = orchestrator_autospawn.validate_continuity_contract({"goal": "x"})

        self.assertTrue(any("disposition" in err for err in errors))
        self.assertTrue(any("promotion_target" in err for err in errors))
        self.assertTrue(any("branch_outcome_class" in err for err in errors))

    def test_extract_dispatch_membrane_evidence_detects_continuity(self):
        req = {
            "id": "spawn-01",
            "prompt_context": {
                "branch_outcome_class": "policy-relevant",
                "capability_lane": "continuity",
                "memory_artifact_ids": ["memory/2026-03-29.md#L1-L12"],
            },
        }

        evidence = orchestrator_autospawn._extract_dispatch_membrane_evidence(req)

        self.assertTrue(evidence["continuity_relevant"])
        self.assertTrue(evidence["memory_consulted"])
        self.assertEqual(evidence["memory_artifact_ids"], ["memory/2026-03-29.md#L1-L12"])
        self.assertEqual(
            evidence["governance_policy_ref"],
            "spine/membranes/governance-runtime-v1.yaml",
        )
        self.assertEqual(
            evidence["memory_policy_ref"],
            "spine/membranes/memory-dispatch-v1.yaml",
        )

    def test_extract_dispatch_membrane_evidence_separates_continuity_from_consultation(self):
        req = {
            "id": "spawn-01",
            "prompt_context": {
                "capability_lane": "continuity",
            },
        }

        evidence = orchestrator_autospawn._extract_dispatch_membrane_evidence(req)

        self.assertTrue(evidence["continuity_relevant"])
        self.assertFalse(evidence["memory_consulted"])
        self.assertEqual(evidence["memory_artifact_ids"], [])
        self.assertEqual(
            evidence["memory_policy_ref"],
            "spine/membranes/memory-dispatch-v1.yaml",
        )

    def test_append_dispatch_log_rejects_inconsistent_memory_fields(self):
        entry = {
            "ts": "2026-03-30T12:00:00",
            "event": "spawn_dispatched",
            "id": "spawn-01",
            "ok": True,
            "control_mode": "control-affecting",
            "governance_policy_ref": "spine/membranes/governance-runtime-v1.yaml",
            "continuity_relevant": False,
            "memory_consulted": False,
            "memory_artifact_ids": ["memory/2026-03-29.md#L1"],
        }

        with self.assertRaisesRegex(ValueError, "memory_consulted=false"):
            orchestrator_autospawn.append_dispatch_log(entry)

    def test_append_dispatch_log_rejects_control_without_governance_ref(self):
        entry = {
            "ts": "2026-03-30T12:00:00",
            "event": "spawn_dispatched",
            "id": "spawn-01",
            "ok": True,
            "control_mode": "control-affecting",
            "continuity_relevant": False,
            "memory_consulted": False,
            "memory_artifact_ids": [],
        }

        with self.assertRaisesRegex(ValueError, "governance_policy_ref"):
            orchestrator_autospawn.append_dispatch_log(entry)

    def test_append_dispatch_log_rejects_memory_policy_ref_when_not_relevant(self):
        entry = {
            "ts": "2026-03-30T12:00:00",
            "event": "spawn_dispatched",
            "id": "spawn-01",
            "ok": True,
            "control_mode": "descriptive",
            "continuity_relevant": False,
            "memory_consulted": False,
            "memory_artifact_ids": [],
            "memory_policy_ref": "spine/membranes/memory-dispatch-v1.yaml",
        }

        with self.assertRaisesRegex(ValueError, "memory_policy_ref may only appear"):
            orchestrator_autospawn.append_dispatch_log(entry)

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
        requests = [
            {
                "id": "spawn-01",
                "lane": "sandy-builder",
                "prompt_context": {
                    "branch_outcome_class": "policy-relevant",
                    "capability_lane": "continuity",
                    "disposition": "POLICY_PROMOTE",
                    "promotion_target": "tests/config",
                    "memory_artifact_ids": ["memory/2026-03-29.md#L10-L16"],
                },
                "spawn": {"runtime": "subagent", "task": "x"},
            }
        ]

        with patch.object(orchestrator_autospawn, "resolve_openclaw_command", return_value=["openclaw"]), \
             patch.object(orchestrator_autospawn, "append_dispatch_log") as mock_log, \
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

            log_payload = mock_log.call_args[0][0]
            self.assertEqual(log_payload["control_mode"], "control-affecting")
            self.assertTrue(log_payload["continuity_relevant"])
            self.assertTrue(log_payload["memory_consulted"])
            self.assertEqual(log_payload["memory_artifact_ids"], ["memory/2026-03-29.md#L10-L16"])
            self.assertEqual(
                log_payload["governance_policy_ref"],
                "spine/membranes/governance-runtime-v1.yaml",
            )
            self.assertEqual(
                log_payload["memory_policy_ref"],
                "spine/membranes/memory-dispatch-v1.yaml",
            )

    def test_dispatch_dry_run_marks_dispatched_without_subprocess(self):
        requests = [{
            "id": "spawn-01",
            "prompt_context": {
                "branch_outcome_class": "local",
                "disposition": "LOG_ONLY",
                "promotion_target": "log-only",
            },
            "spawn": {"runtime": "subagent", "task": "x"},
        }]

        with patch.object(orchestrator_autospawn, "resolve_openclaw_command", return_value=["openclaw"]), \
             patch.object(orchestrator_autospawn, "append_dispatch_log") as mock_log, \
             patch("scripts.orchestrator_autospawn.subprocess.run") as mock_run:
            out = orchestrator_autospawn.dispatch_spawn_requests(requests, dry_run=True)

            self.assertEqual(out["attempted"], 1)
            self.assertEqual(out["dispatched"], 1)
            self.assertEqual(len(out["errors"]), 0)
            mock_run.assert_not_called()

            self.assertEqual(out["results"][0]["control_mode"], "control-affecting")
            self.assertFalse(out["results"][0]["continuity_relevant"])
            self.assertFalse(out["results"][0]["memory_consulted"])
            self.assertEqual(out["results"][0]["memory_artifact_ids"], [])
            self.assertNotIn("memory_policy_ref", out["results"][0])

            log_payload = mock_log.call_args[0][0]
            self.assertEqual(log_payload["control_mode"], "control-affecting")
            self.assertFalse(log_payload["continuity_relevant"])
            self.assertEqual(
                log_payload["governance_policy_ref"],
                "spine/membranes/governance-runtime-v1.yaml",
            )
            self.assertNotIn("memory_policy_ref", log_payload)

    def test_dispatch_rejects_missing_disposition_and_target(self):
        requests = [{"id": "spawn-01", "prompt_context": {}, "spawn": {"runtime": "subagent", "task": "x"}}]

        with patch.object(orchestrator_autospawn, "resolve_openclaw_command", return_value=["openclaw"]), \
             patch("scripts.orchestrator_autospawn.subprocess.run") as mock_run:
            out = orchestrator_autospawn.dispatch_spawn_requests(requests, dry_run=False)

            self.assertEqual(out["attempted"], 1)
            self.assertEqual(out["dispatched"], 0)
            self.assertTrue(any("disposition" in err for err in out["errors"]))
            self.assertTrue(any("promotion_target" in err for err in out["errors"]))
            mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
