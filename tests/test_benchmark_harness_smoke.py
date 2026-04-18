import unittest

from nfem_suite.benchmarks.temporal_predictive_processing import make_default_harness


class BenchmarkHarnessSmokeTests(unittest.TestCase):
    def test_scaffold_exposes_three_variant_interfaces(self):
        harness = make_default_harness()

        interfaces = harness.variant_interfaces()

        self.assertEqual(
            list(interfaces.keys()),
            [
                "single-scale-baseline",
                "multiframe-unconstrained-baseline",
                "neighbor-only-contract-model",
            ],
        )
        for variant_id, interface_contract in interfaces.items():
            self.assertTrue(interface_contract, msg=f"missing interface for {variant_id}")


if __name__ == "__main__":
    unittest.main()
