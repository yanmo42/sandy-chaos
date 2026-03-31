import unittest

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

        contract = automation_orchestrator.task_contract(item, cfg=cfg)

        self.assertIn("memory_artifact_ids", contract)
        self.assertIn("spine/subsystems/SC-SUBSYSTEM-0001-topological-memory-v0.yaml", contract["memory_artifact_ids"])
        self.assertIn("spine/membranes/memory-dispatch-v1.yaml", contract["memory_artifact_ids"])
        self.assertIn("memory/research/topological-memory-v0/comparison_summary_v0.json", contract["memory_artifact_ids"])
        self.assertEqual(contract["disposition"], "POLICY_PROMOTE")
        self.assertEqual(contract["promotion_target"], "tests/config")
        self.assertEqual(contract["branch_outcome_class"], "policy-relevant")
        self.assertEqual(contract["promotion_review_requirement"], "human-review")
        self.assertEqual(contract["promotion_review_status"], "pending")
        self.assertIn("continuity_context", contract)
        self.assertIn("topological_memory_signal", contract["continuity_context"])

    def test_validate_task_contracts_requires_disposition_and_target(self):
        errors = automation_orchestrator.validate_task_contracts(
            [{"goal": "broken", "disposition": "", "promotion_target": ""}]
        )

        self.assertTrue(any("disposition" in err for err in errors))
        self.assertTrue(any("promotion_target" in err for err in errors))
        self.assertTrue(any("branch_outcome_class" in err for err in errors))
        self.assertTrue(any("promotion_review_requirement" in err for err in errors))
        self.assertTrue(any("promotion_review_status" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
