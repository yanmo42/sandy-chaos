import tempfile
import unittest
from datetime import datetime
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


class SelfImproveTelegramPolicyTests(unittest.TestCase):
    def test_quiet_hours_blocks_send(self):
        state = {"sent": {"daily": {}, "weekly": {}}}
        cfg = {
            "quietHours": {"start": "23:00", "end": "08:00"},
            "prefixes": {"daily": "[SANDY-DAILY]", "weekly": "[SANDY-WEEKLY]"},
            "rateLimits": {"dailyMax": 1, "weeklyMax": 1},
        }
        now = datetime.fromisoformat("2026-03-02T23:30:00")
        allowed, reason, kind = self_improve._can_send_now("[SANDY-DAILY] hi", state, cfg, now)
        self.assertFalse(allowed)
        self.assertIn("quiet hours", reason.lower())
        self.assertIsNone(kind)

    def test_daily_rate_limit_enforced_per_day(self):
        state = {"sent": {"daily": {"window": "2026-03-02", "count": 1}}}
        cfg = {
            "prefixes": {"daily": "[SANDY-DAILY]", "weekly": "[SANDY-WEEKLY]"},
            "rateLimits": {"dailyMax": 1, "weeklyMax": 1},
        }
        now = datetime.fromisoformat("2026-03-02T12:00:00")
        allowed, reason, kind = self_improve._can_send_now("[SANDY-DAILY] hi", state, cfg, now)
        self.assertFalse(allowed)
        self.assertEqual(kind, "daily")
        self.assertIn("rate limit", reason.lower())

        next_day = datetime.fromisoformat("2026-03-03T09:00:00")
        allowed2, reason2, kind2 = self_improve._can_send_now("[SANDY-DAILY] hi", state, cfg, next_day)
        self.assertTrue(allowed2)
        self.assertIsNone(reason2)
        self.assertEqual(kind2, "daily")
