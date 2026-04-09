import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import automation_orchestrator


class AutomationOrchestratorValidationConfigTests(unittest.TestCase):
    def test_resolve_promotion_review_policy_by_target(self):
        cfg = {
            "promotionReview": {
                "defaultRequirement": "human-review",
                "defaultStatus": "pending",
                "byTarget": {
                    "todo": {"requirement": "not-required", "status": "not-required"},
                    "workflow": {"requirement": "human-review", "status": "pending"},
                },
            }
        }

        todo_policy = automation_orchestrator.resolve_promotion_review_policy(cfg, "todo")
        workflow_policy = automation_orchestrator.resolve_promotion_review_policy(cfg, "workflow")

        self.assertEqual(todo_policy, {"requirement": "not-required", "status": "not-required"})
        self.assertEqual(workflow_policy, {"requirement": "human-review", "status": "pending"})

    def test_resolve_validation_command_by_lane(self):
        cfg = {
            "validation": {
                "commands": {
                    "default": ["python -m unittest discover -s tests -q"],
                    "byLane": {
                        "sandy-planner": ["python3 scripts/todo_scan.py plans/todo.md"],
                    },
                }
            }
        }

        planner = automation_orchestrator.resolve_validation_command(cfg, lane="sandy-planner")
        builder = automation_orchestrator.resolve_validation_command(cfg, lane="sandy-builder")

        self.assertEqual(planner, "python3 scripts/todo_scan.py plans/todo.md")
        self.assertEqual(builder, "python -m unittest discover -s tests -q")

    def test_capability_lane_recognizes_continuity_work(self):
        item = automation_orchestrator.TodoItem(
            state="open",
            text="Integrate topological memory retrieval into planner context",
            section="Continuity",
        )

        self.assertEqual(automation_orchestrator.capability_lane_for_item(item), "continuity")

    def test_task_contract_includes_validation_policy_ref(self):
        item = automation_orchestrator.TodoItem(
            state="open",
            text="Document claim tier constraints",
            section="Docs",
        )
        cfg = {
            "validation": {
                "commands": {
                    "default": ["python -m unittest discover -s tests -q"],
                    "byLane": {
                        "sandy-planner": ["python3 scripts/todo_scan.py plans/todo.md"],
                    },
                }
            }
        }

        contract = automation_orchestrator.task_contract(item, cfg=cfg)
        self.assertIn("validation_command", contract)
        self.assertIn("validation_policy_ref", contract)
        self.assertEqual(contract["validation_policy_ref"]["config"], "config/orchestrator.json")
        self.assertEqual(contract["disposition"], "DOC_PROMOTE")
        self.assertEqual(contract["promotion_target"], "docs")
        self.assertEqual(contract["branch_outcome_class"], "promotable")
        self.assertEqual(contract["promotion_review_requirement"], "human-review")
        self.assertEqual(contract["promotion_review_status"], "pending")

    def test_task_contract_attaches_continuity_artifact_ids(self):
        item = automation_orchestrator.TodoItem(
            state="open",
            text="Integrate topological memory retrieval into planner context",
            section="Continuity",
        )
        cfg = {
            "validation": {
                "commands": {
                    "default": ["python -m unittest discover -s tests -q"],
                }
            }
        }

        mock_trace = type(
            "Trace",
            (),
            {
                "mode_requested": "auto",
                "mode_used": "topology",
                "baseline_mode": "topology",
                "fallback_reason": None,
                "authority_note": "Advisory continuity context only.",
                "retrieval_trace_artifact": "memory/research/topological-memory-v0/runtime_traces/sample.json",
                "ranked_results": [{"node_id": "N_SCRIPT_AUTOMATION_ORCH", "score": 1.0}],
            },
        )()
        with patch.object(automation_orchestrator, "write_retrieval_trace", return_value=mock_trace):
            contract = automation_orchestrator.task_contract(item, cfg=cfg)

        self.assertIn("memory_artifact_ids", contract)
        self.assertIn("spine/subsystems/SC-SUBSYSTEM-0001-topological-memory-v0.yaml", contract["memory_artifact_ids"])
        self.assertIn("spine/membranes/memory-dispatch-v1.yaml", contract["memory_artifact_ids"])
        self.assertIn("memory/research/topological-memory-v0/comparison_summary_v0.json", contract["memory_artifact_ids"])
        self.assertIn("memory/research/topological-memory-v0/runtime_traces/sample.json", contract["memory_artifact_ids"])
        self.assertEqual(contract["disposition"], "POLICY_PROMOTE")
        self.assertEqual(contract["promotion_target"], "tests/config")
        self.assertEqual(contract["branch_outcome_class"], "policy-relevant")
        self.assertEqual(contract["promotion_review_requirement"], "human-review")
        self.assertEqual(contract["promotion_review_status"], "pending")
        self.assertIn("continuity_context", contract)
        self.assertIn("topological_memory_signal", contract["continuity_context"])
        self.assertIn("topological_retrieval", contract["continuity_context"])
        self.assertEqual(contract["continuity_context"]["topological_retrieval"]["mode_used"], "topology")
        self.assertEqual(
            contract["continuity_context"]["topological_retrieval"]["retrieval_trace_artifact"],
            "memory/research/topological-memory-v0/runtime_traces/sample.json",
        )

    def test_validate_task_contracts_requires_disposition_and_target(self):
        errors = automation_orchestrator.validate_task_contracts(
            [{"goal": "broken", "disposition": "", "promotion_target": ""}]
        )

        self.assertTrue(any("disposition" in err for err in errors))
        self.assertTrue(any("promotion_target" in err for err in errors))
        self.assertTrue(any("branch_outcome_class" in err for err in errors))
        self.assertTrue(any("promotion_review_requirement" in err for err in errors))
        self.assertTrue(any("promotion_review_status" in err for err in errors))


class SessionResumeContextTests(unittest.TestCase):
    def test_load_session_resume_context_returns_none_when_empty(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = automation_orchestrator.load_session_resume_context(Path(td))
        self.assertIsNone(ctx)

    def test_load_session_resume_context_from_checkpoint(self):
        from nfem_suite.intelligence.ygg.continuity import write_checkpoint
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_checkpoint(
                root,
                lane="ops",
                summary="Ops lane stable",
                disposition="LOG_ONLY",
                next_action="proceed to validation",
            )
            ctx = automation_orchestrator.load_session_resume_context(root)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["type"], "checkpoint")
        self.assertEqual(ctx["lane"], "ops")
        self.assertEqual(ctx["next_action"], "proceed to validation")

    def test_load_session_resume_context_prefers_resume_over_checkpoint(self):
        from nfem_suite.intelligence.ygg.continuity import write_checkpoint, write_resume_artifact
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_checkpoint(
                root,
                lane="ops",
                summary="Earlier checkpoint",
                disposition="LOG_ONLY",
                next_action="stale action",
            )
            write_resume_artifact(
                root,
                lane="continuity",
                branch_purpose="Wire the consumer",
                current_state="Half done",
                branch_outcome_class="policy-relevant",
                disposition="POLICY_PROMOTE",
                promotion_target="tests/config",
                next_action="finish wiring",
            )
            ctx = automation_orchestrator.load_session_resume_context(root)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["type"], "resume")
        self.assertEqual(ctx["lane"], "continuity")
        self.assertEqual(ctx["branch_purpose"], "Wire the consumer")
        self.assertEqual(ctx["next_action"], "finish wiring")

    def test_task_contract_attaches_session_resume(self):
        item = automation_orchestrator.TodoItem(
            state="open",
            text="Fix dispatch validation",
            section="Ops",
        )
        cfg = {
            "validation": {"commands": {"default": ["python -m unittest discover -s tests -q"]}}
        }
        mock_resume = {
            "type": "checkpoint",
            "timestamp": "2026-03-26T16:59:58+00:00",
            "lane": "Symbolic Maps",
            "summary": "Lane stabilized",
            "next_action": "extend Ygg promote flows",
        }
        with patch.object(automation_orchestrator, "load_session_resume_context", return_value=mock_resume), \
             patch.object(automation_orchestrator, "load_topological_memory_signal", return_value=None):
            contract = automation_orchestrator.task_contract(item, cfg=cfg)
        self.assertIn("continuity_context", contract)
        self.assertEqual(contract["continuity_context"]["session_resume"], mock_resume)

    def test_task_contract_keeps_fallback_when_runtime_retrieval_fails(self):
        item = automation_orchestrator.TodoItem(
            state="open",
            text="Integrate topological memory retrieval into planner context",
            section="Continuity",
        )
        cfg = {
            "validation": {"commands": {"default": ["python -m unittest discover -s tests -q"]}}
        }
        with patch.object(automation_orchestrator, "write_retrieval_trace", side_effect=FileNotFoundError("missing graph")), \
             patch.object(automation_orchestrator, "load_session_resume_context", return_value=None), \
             patch.object(automation_orchestrator, "load_topological_memory_signal", return_value=None):
            contract = automation_orchestrator.task_contract(item, cfg=cfg)

        self.assertIn("memory_artifact_ids", contract)
        self.assertNotIn("runtime_traces", " ".join(contract["memory_artifact_ids"]))
        self.assertIn("continuity_context", contract)
        self.assertFalse(contract["continuity_context"]["topological_retrieval"]["available"])
        self.assertIn("Workflow continues without runtime retrieval", contract["continuity_context"]["topological_retrieval"]["fallback_behavior"])

    def test_task_contract_omits_continuity_context_when_nothing_loaded(self):
        item = automation_orchestrator.TodoItem(
            state="open",
            text="Fix dispatch validation",
            section="Ops",
        )
        cfg = {
            "validation": {"commands": {"default": ["python -m unittest discover -s tests -q"]}}
        }
        with patch.object(automation_orchestrator, "load_session_resume_context", return_value=None), \
             patch.object(automation_orchestrator, "load_topological_memory_signal", return_value=None):
            contract = automation_orchestrator.task_contract(item, cfg=cfg)
        self.assertNotIn("continuity_context", contract)

    def test_continuity_artifact_ids_includes_session_artifact_paths(self):
        from nfem_suite.intelligence.ygg.continuity import write_checkpoint
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_checkpoint(
                root,
                lane="continuity",
                summary="Checkpoint for test",
                disposition="LOG_ONLY",
                next_action="proceed",
            )
            item = automation_orchestrator.TodoItem(
                state="open",
                text="Integrate topological memory retrieval into planner context",
                section="Continuity",
            )
            refs = automation_orchestrator.continuity_artifact_ids_for_item(item, root=root)
        checkpoint_refs = [r for r in refs if "checkpoints" in r]
        self.assertEqual(len(checkpoint_refs), 1)
        self.assertTrue(checkpoint_refs[0].startswith("state/ygg/checkpoints/"))


if __name__ == "__main__":
    unittest.main()
