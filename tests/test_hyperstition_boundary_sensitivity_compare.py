import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.hyperstition_boundary_sensitivity_compare import parse_args, run


class TestHyperstitionBoundarySensitivityCompare(unittest.TestCase):
    def test_small_grid_reports_profiles_and_metrics(self):
        args = parse_args([
            "--grid", "9",
            "--initial-grid", "3",
            "--steps", "20",
            "--clean-gap-threshold", "0.1",
        ])
        results = run(args)

        self.assertEqual(results["pass"], "hyperstition_boundary_sensitivity_compare")
        self.assertIn("arm_a_narrative_on", results["profiles"])
        self.assertIn("arm_e_open_loop_temporal_driver", results["profiles"])
        self.assertIn("boundary_edge_fraction", results["separation_metrics"])
        self.assertIn("mean_initial_sensitivity", results["separation_metrics"])
        self.assertIn(results["verdict"], {"CANDIDATE_SEPARATOR_FOUND", "NO_CLEAN_SEPARATOR_FOUND"})

        for profile in results["profiles"].values():
            boundary = profile["boundary_geometry"]
            sensitivity = profile["initial_condition_sensitivity"]
            self.assertGreater(boundary["adjacent_edge_count"], 0)
            self.assertEqual(len(sensitivity["by_initial"]), 3)


if __name__ == "__main__":
    unittest.main()
