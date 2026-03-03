import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scripts import self_improve


class ResearchCycleSummaryHookTests(unittest.TestCase):
    def test_summary_is_generated_for_active_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            research = root / "memory" / "research"
            research.mkdir(parents=True, exist_ok=True)

            base = "2026-03-03-frame-asymmetry"
            (research / f"{base}-query.md").write_text("# Query\n", encoding="utf-8")
            (research / f"{base}-evidence.csv").write_text(
                "source_id,url_or_doi,claim_supported\n"
                "S001,https://example.com/a,Claim A\n"
                "S002,https://example.com/b,Claim B\n",
                encoding="utf-8",
            )
            (research / f"{base}-synthesis.md").write_text(
                "# Synthesis\n\n## Claims\n- Claim A [S001]\n- Claim B [S002]\n",
                encoding="utf-8",
            )
            (research / f"{base}-falsification.md").write_text("# Falsification\n", encoding="utf-8")

            original_root = self_improve.ROOT
            original_research = self_improve.RESEARCH_DIR
            try:
                self_improve.ROOT = root
                self_improve.RESEARCH_DIR = research
                result = self_improve.maybe_write_research_cycle_summary(
                    dry_run=False,
                    now=datetime(2026, 3, 3, 10, 0, 0),
                )
            finally:
                self_improve.ROOT = original_root
                self_improve.RESEARCH_DIR = original_research

            self.assertTrue(result["active"])
            self.assertTrue(result["generated"])
            summary_path = Path(result["path"])
            self.assertTrue(summary_path.exists())
            text = summary_path.read_text(encoding="utf-8")
            self.assertIn("evidence rows: 2", text)
            self.assertIn("synthesis claims bullets: 2", text)
            self.assertIn("no retrocausal claim", text)

    def test_summary_not_generated_when_cycle_inactive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            research = root / "memory" / "research"
            research.mkdir(parents=True, exist_ok=True)

            base = "2026-03-03-inactive"
            (research / f"{base}-query.md").write_text("# Query\n", encoding="utf-8")
            (research / f"{base}-evidence.csv").write_text("source_id\nS001\n", encoding="utf-8")
            (research / f"{base}-synthesis.md").write_text("# Synthesis\n", encoding="utf-8")
            (research / f"{base}-falsification.md").write_text("# Falsification\n", encoding="utf-8")

            stale = datetime(2026, 2, 20, 10, 0, 0).timestamp()
            for p in research.iterdir():
                p.touch()
                import os
                os.utime(p, (stale, stale))

            original_root = self_improve.ROOT
            original_research = self_improve.RESEARCH_DIR
            try:
                self_improve.ROOT = root
                self_improve.RESEARCH_DIR = research
                result = self_improve.maybe_write_research_cycle_summary(
                    dry_run=False,
                    now=datetime(2026, 3, 3, 10, 0, 0),
                )
            finally:
                self_improve.ROOT = original_root
                self_improve.RESEARCH_DIR = original_research

            self.assertFalse(result["active"])
            self.assertFalse(result["generated"])
            self.assertIsNone(result["path"])


if __name__ == "__main__":
    unittest.main()
