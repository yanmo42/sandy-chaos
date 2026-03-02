import tempfile
import unittest
from pathlib import Path

from scripts import self_improve


class SelfImproveNotificationTemplateTests(unittest.TestCase):
    def test_build_cadence_notification_renders_daily_and_weekly_templates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            templates = root / "templates"
            templates.mkdir(parents=True, exist_ok=True)

            daily_tpl = templates / "daily_digest_notification.md"
            weekly_tpl = templates / "weekly_digest_notification.md"
            daily_tpl.write_text("daily={{date}} file={{artifact}}", encoding="utf-8")
            weekly_tpl.write_text("weekly={{week_label}} file={{artifact}}", encoding="utf-8")

            original_daily = self_improve.DAILY_DIGEST_TEMPLATE
            original_weekly = self_improve.WEEKLY_DIGEST_TEMPLATE
            try:
                self_improve.DAILY_DIGEST_TEMPLATE = daily_tpl
                self_improve.WEEKLY_DIGEST_TEMPLATE = weekly_tpl

                text = self_improve.build_cadence_notification(
                    ["/tmp/2026-03-02-meso-review.md", "/tmp/2026-W10-slow-distill.md"]
                )
            finally:
                self_improve.DAILY_DIGEST_TEMPLATE = original_daily
                self_improve.WEEKLY_DIGEST_TEMPLATE = original_weekly

            self.assertIn("daily=", text)
            self.assertIn("file=2026-03-02-meso-review.md", text)
            self.assertIn("weekly=", text)
            self.assertIn("file=2026-W10-slow-distill.md", text)


if __name__ == "__main__":
    unittest.main()
