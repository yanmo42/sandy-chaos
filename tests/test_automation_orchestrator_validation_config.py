import unittest

from scripts import automation_orchestrator


class AutomationOrchestratorValidationConfigTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
