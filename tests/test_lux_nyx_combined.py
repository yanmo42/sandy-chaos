"""Tests for Lux–Nyx combined shape and route pipeline."""

import tempfile
import unittest
from pathlib import Path

from nfem_suite.intelligence.narrative_invariants.lux_nyx_governance import (
    GovernanceOutcome,
)
from nfem_suite.intelligence.narrative_invariants.lux_nyx_pilot import (
    LuxNyxCombinedOutcome,
    shape_and_route,
)


class LuxNyxCombinedTests(unittest.TestCase):
    def test_shape_and_route_returns_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            outcome = shape_and_route(
                "Review the continuity artifacts for the current sprint",
                section="continuity",
                root=td,
            )
            self.assertIsInstance(outcome, LuxNyxCombinedOutcome)
            self.assertEqual(outcome.governance.destination, "surface")
            self.assertTrue(outcome.governance.artifact_path.exists())
            self.assertIn("governance", str(outcome.governance.artifact_path))
            self.assertTrue(outcome.shadow_path.exists())
            self.assertIn("shadow", str(outcome.shadow_path))

    def test_shape_and_route_writes_both_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outcome = shape_and_route(
                "Canonize this speculative hypothesis about the shadow persona",
                section="mythic",
                root=td,
            )
            # speculative + canon/symbolic-input → risk=high → action=refuse-with-reason → refusal-log
            self.assertEqual(outcome.governance.destination, "refusal-log")

            # Check shadow artifact (Phase 2)
            self.assertTrue(outcome.shadow_path.exists())

            # Check governance artifact (Phase 3)
            self.assertTrue(outcome.governance.artifact_path.exists())

    def test_shape_and_route_keeps_single_causal_chain(self):
        with tempfile.TemporaryDirectory() as td:
            outcome = shape_and_route(
                "Route this continuity blocker to the right lane now",
                section="continuity",
                root=td,
            )
            self.assertEqual(outcome.recommendation.action, "route")
            self.assertEqual(outcome.record.input_type, "route-request")
            self.assertEqual(outcome.governance.destination, "route-queue")
            self.assertEqual(
                outcome.recommendation.shadow_artifact_type,
                outcome.record.shadow_artifact_type,
            )

    def test_shape_and_route_governance_artifact_matches_shaping_output(self):
        with tempfile.TemporaryDirectory() as td:
            outcome = shape_and_route(
                "Review the continuity artifacts for the active blocker",
                section="continuity",
                root=td,
            )
            artifact = outcome.governance.artifact_path.read_text()
            self.assertIn(f'"evaluator_action": "{outcome.recommendation.action}"', artifact)
            self.assertIn(
                f'"shadow_artifact_type": "{outcome.recommendation.shadow_artifact_type}"',
                artifact,
            )
