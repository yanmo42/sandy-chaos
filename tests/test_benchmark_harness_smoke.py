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

    def test_benchmark_case_rejects_retrocausal_frame_order(self):
        # Frames must be supplied in non-decreasing timestep order. A later
        # frame_id carrying an earlier timestep would let a variant index a
        # "future" observation while pretending it was a past one.
        earlier = BenchmarkFrame(
            frame_id="past",
            timestep=2,
            observed_state={"signal": 0.0},
        )
        later = BenchmarkFrame(
            frame_id="before-past",
            timestep=1,
            observed_state={"signal": 0.0},
        )
        with self.assertRaises(ValueError):
            BenchmarkCase(
                case_id="retrocausal",
                description="non-monotonic timesteps must fail loudly",
                frames=(earlier, later),
                target_state={"signal": 0.0},
            )

    def test_neighbor_only_variant_refuses_case_without_topology_metadata(self):
        # The neighbor-only contract model declares that neighbor topology
        # metadata is a precondition. Without it, the scaffold must refuse the
        # case instead of silently emitting a "scaffold-only" pass.
        from nfem_suite.benchmarks.temporal_predictive_processing import (
            make_default_harness,
            make_smoke_case,
        )

        harness = make_default_harness()
        neighbor_variant = next(
            v for v in harness.variants if v.variant_id == "neighbor-only-contract-model"
        )

        base_case = make_smoke_case()
        stripped_metadata = {
            k: v for k, v in base_case.metadata.items() if k != "neighbor_topology"
        }
        bad_case = BenchmarkCase(
            case_id=base_case.case_id,
            description=base_case.description,
            frames=base_case.frames,
            target_state=base_case.target_state,
            metadata=stripped_metadata,
        )

        result = neighbor_variant.run(bad_case)

        self.assertEqual(result.status, "scaffold-only-contract-unmet")
        self.assertIn("neighbor_topology", result.summary)
        self.assertEqual(
            result.placeholder_metrics["missing_metadata_keys"], ["neighbor_topology"]
        )
        self.assertIsNone(result.placeholder_metrics["prediction_error"])


if __name__ == "__main__":
    unittest.main()
