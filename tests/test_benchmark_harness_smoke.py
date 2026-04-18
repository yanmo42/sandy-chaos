import unittest

from nfem_suite.benchmarks.temporal_predictive_processing import make_default_harness


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


if __name__ == "__main__":
    unittest.main()
