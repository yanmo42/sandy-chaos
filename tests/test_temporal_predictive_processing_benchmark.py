import unittest

from nfem_suite.benchmarks.temporal_predictive_processing import (
    BenchmarkCase,
    make_default_harness,
    make_smoke_case,
)


class TemporalPredictiveProcessingBenchmarkScaffoldTests(unittest.TestCase):
    def test_default_harness_exposes_canonical_variant_interfaces(self):
        harness = make_default_harness()

        self.assertEqual(
            [variant.variant_id for variant in harness.variants],
            [
                "single-scale-baseline",
                "multiframe-unconstrained-baseline",
                "neighbor-only-contract-model",
            ],
        )

        described = harness.describe()
        self.assertEqual(described["status"], "scaffold-only")
        self.assertEqual(len(described["variants"]), 3)
        self.assertIn("No empirical results", " ".join(described["notes"]))

    def test_smoke_case_runs_without_claiming_scores(self):
        harness = make_default_harness()

        results = harness.run_smoke_case()

        self.assertEqual(len(results), 3)
        for result in results:
            self.assertEqual(result.status, "scaffold-only")
            self.assertIsNone(result.placeholder_metrics["prediction_error"])
            self.assertGreater(result.placeholder_metrics["case_frame_count"], 0)
            self.assertIn("does not emit empirical scores yet", result.summary)

    def test_case_validation_rejects_duplicate_frame_ids(self):
        frame = make_smoke_case().frames[0]
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="duplicate-frames",
                description="invalid benchmark case",
                frames=(frame, frame),
                target_state={"signal": 1.0},
            )


if __name__ == "__main__":
    unittest.main()
