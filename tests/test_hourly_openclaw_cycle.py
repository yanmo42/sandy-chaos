import unittest

from scripts import hourly_openclaw_cycle


class HourlyOpenclawCycleTests(unittest.TestCase):
    def test_maybe_commit_dry_run_reports_not_committed(self):
        committed, message = hourly_openclaw_cycle.maybe_commit(["README.md"], dry_run=True)

        self.assertFalse(committed)
        self.assertIsNotNone(message)
        self.assertTrue(message.startswith("chore: hourly automation cycle "))

    def test_maybe_commit_no_changes(self):
        committed, message = hourly_openclaw_cycle.maybe_commit([], dry_run=True)

        self.assertFalse(committed)
        self.assertIsNone(message)


if __name__ == "__main__":
    unittest.main()
