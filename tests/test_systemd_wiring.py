import unittest
from pathlib import Path


class SystemdWiringTests(unittest.TestCase):
    def test_automation_service_uses_activation_gate_wrapper(self):
        service_path = Path("ops/systemd/sandy-automation.service")
        text = service_path.read_text(encoding="utf-8")

        execstart = next(
            (line for line in text.splitlines() if line.startswith("ExecStart=")),
            "",
        )

        self.assertIn("scripts/automation_activation_gate.py", execstart)

    def test_automation_service_loads_fallback_automation_env(self):
        service_path = Path("ops/systemd/sandy-automation.service")
        text = service_path.read_text(encoding="utf-8")
        self.assertIn("EnvironmentFile=-%h/.config/sandy-chaos/automation.env", text)


if __name__ == "__main__":
    unittest.main()
