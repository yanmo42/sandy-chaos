import unittest
from pathlib import Path


class SystemdWiringTests(unittest.TestCase):
    def test_automation_service_enables_telegram_digest_delivery(self):
        service_path = Path("ops/systemd/sandy-automation.service")
        text = service_path.read_text(encoding="utf-8")

        execstart = next(
            (line for line in text.splitlines() if line.startswith("ExecStart=")),
            "",
        )

        self.assertIn("scripts/self_improve.py full-pass", execstart)
        self.assertIn("--send-telegram", execstart)


if __name__ == "__main__":
    unittest.main()
