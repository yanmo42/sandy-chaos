import tempfile
import unittest
from pathlib import Path

from scripts import research_verifier


class ResearchVerifierTests(unittest.TestCase):
    def test_verify_passes_when_all_claims_have_valid_source_tags(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = root / "evidence.csv"
            synthesis = root / "synthesis.md"

            evidence.write_text(
                "source_id,url_or_doi,claim_supported\n"
                "S001,https://example.com/a,Claim A\n"
                "S002,https://example.com/b,Claim B\n",
                encoding="utf-8",
            )
            synthesis.write_text(
                "# Synthesis\n\n"
                "## Claims\n"
                "- Claim A supported by strong evidence [S001]\n"
                "- Claim B replicated across studies [S001][S002]\n",
                encoding="utf-8",
            )

            result = research_verifier.verify_claim_source_mapping(synthesis, evidence)
            self.assertTrue(result.ok)
            self.assertEqual(result.claim_lines, 2)
            self.assertEqual(result.claim_lines_with_tags, 2)
            self.assertEqual(result.missing_source_tags, [])
            self.assertEqual(result.unknown_source_ids, [])

    def test_verify_fails_on_missing_tags_and_unknown_ids(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = root / "evidence.csv"
            synthesis = root / "synthesis.md"

            evidence.write_text(
                "source_id,url_or_doi,claim_supported\n"
                "S001,https://example.com/a,Claim A\n",
                encoding="utf-8",
            )
            synthesis.write_text(
                "# Synthesis\n\n"
                "## Claims\n"
                "- Claim A with valid citation [S001]\n"
                "- Claim B missing citation\n"
                "- Claim C uses unknown source [S999]\n",
                encoding="utf-8",
            )

            result = research_verifier.verify_claim_source_mapping(synthesis, evidence)
            self.assertFalse(result.ok)
            self.assertEqual(result.claim_lines, 3)
            self.assertEqual(result.claim_lines_with_tags, 2)
            self.assertEqual(len(result.missing_source_tags), 1)
            self.assertIn("missing citation", result.missing_source_tags[0])
            self.assertEqual(result.unknown_source_ids, ["S999"])


if __name__ == "__main__":
    unittest.main()
