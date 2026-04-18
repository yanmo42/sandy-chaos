import unittest

from nfem_suite.benchmarks.temporal_predictive_processing import (
    BenchmarkCase,
    BenchmarkFrame,
    BenchmarkHarness,
    ScaffoldVariant,
    make_default_harness,
)


class BenchmarkHarnessSmokeTests(unittest.TestCase):
    def test_scaffold_exposes_three_variant_interfaces(self):
        harness = make_default_harness()

        interfaces = harness.variant_interfaces()
        smoke_results = harness.run_smoke_case()

        self.assertEqual(
            list(interfaces.keys()),
            [
                "single-scale-baseline",
                "multiframe-unconstrained-baseline",
                "neighbor-only-contract-model",
            ],
        )
        self.assertEqual(len(smoke_results), 3)

        for variant_id, interface_contract in interfaces.items():
            self.assertTrue(interface_contract, msg=f"missing interface for {variant_id}")

        for result in smoke_results:
            self.assertEqual(result.status, "scaffold-only")
            self.assertIsNone(result.placeholder_metrics["prediction_error"])
            self.assertTrue(
                result.causal_guards,
                msg=f"missing causal guards for {result.variant_id}",
            )
            self.assertTrue(
                result.failure_modes,
                msg=f"missing failure modes for {result.variant_id}",
            )


class BenchmarkHarnessFailureModeTests(unittest.TestCase):
    """Falsification-oriented checks: the scaffold must refuse malformed inputs.

    These tests protect the inspectable-only contract by proving that invalid
    states fail loudly instead of silently accepting ill-formed wiring.
    """

    def test_unknown_variant_id_is_rejected(self):
        with self.assertRaises(ValueError):
            ScaffoldVariant(
                variant_id="not-a-real-variant",
                label="bogus",
                interface_contract=("x",),
                causal_guards=("y",),
                failure_modes=("z",),
            )

    def test_harness_rejects_non_canonical_variant_order(self):
        default = make_default_harness()
        shuffled = (default.variants[2], default.variants[0], default.variants[1])
        with self.assertRaises(ValueError):
            BenchmarkHarness(variants=shuffled)

    def test_benchmark_case_rejects_empty_frames(self):
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="empty",
                description="no frames",
                frames=(),
                target_state={"signal": 0.0},
            )

    def test_benchmark_case_rejects_duplicate_frame_ids(self):
        frame = BenchmarkFrame(
            frame_id="dup",
            timestep=0,
            observed_state={"signal": 0.0},
        )
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="dup-case",
                description="duplicate frame ids",
                frames=(frame, frame),
                target_state={"signal": 0.0},
            )

    def test_benchmark_frame_rejects_negative_latency(self):
        bad_frame = BenchmarkFrame(
            frame_id="f",
            timestep=0,
            observed_state={"signal": 0.0},
            latency=-0.1,
        )
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="neg-latency",
                description="negative latency must fail",
                frames=(bad_frame,),
                target_state={"signal": 0.0},
            )


if __name__ == "__main__":
    unittest.main()
