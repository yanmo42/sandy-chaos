import os
import sys
import unittest

# Add project root to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nfem_suite.intelligence.cognition import HyperstitionParameters, HyperstitionToyModel


class TestHyperstitionDynamics(unittest.TestCase):
    def test_fixed_points_include_unstable_center_and_stable_outer_branches(self):
        params = HyperstitionParameters(
            narrative_inertia=0.9,
            social_coupling=0.2,
            observation_gain=1.0,
            observer_coupling=0.6,
            action_gain=2.0,
            temporal_bias_gain=1.0,
            noise_std=0.0,
        )
        model = HyperstitionToyModel(params=params)

        fps = model.find_fixed_points(exogenous_truth=0.0, temporal_asymmetry=0.0)
        self.assertGreaterEqual(len(fps), 3)

        center = min(fps, key=lambda fp: abs(fp.value))
        self.assertAlmostEqual(center.value, 0.0, delta=0.05)
        self.assertFalse(center.stable)

        stable_outer = [fp for fp in fps if fp.stable and abs(fp.value) > 0.3]
        self.assertGreaterEqual(len(stable_outer), 2)

    def test_temporal_asymmetry_breaks_neutral_symmetry(self):
        model = HyperstitionToyModel()

        neutral = model.rollout_mean_field(
            initial_m=0.0,
            steps=40,
            exogenous_truth=0.0,
            temporal_asymmetry=0.0,
        )
        positive = model.rollout_mean_field(
            initial_m=0.0,
            steps=40,
            exogenous_truth=0.0,
            temporal_asymmetry=0.2,
        )
        negative = model.rollout_mean_field(
            initial_m=0.0,
            steps=40,
            exogenous_truth=0.0,
            temporal_asymmetry=-0.2,
        )

        self.assertAlmostEqual(float(neutral[-1]), 0.0, delta=1e-7)
        self.assertGreater(float(positive[-1]), 0.4)
        self.assertLess(float(negative[-1]), -0.4)

    def test_positive_temporal_lead_can_create_self_fulfilling_regime(self):
        params = HyperstitionParameters(
            narrative_inertia=0.3,
            social_coupling=0.0,
            observation_gain=1.4,
            observer_coupling=0.9,
            action_gain=2.5,
            temporal_bias_gain=3.0,
            noise_std=0.0,
        )
        model = HyperstitionToyModel(params=params)

        initial_m = 0.6
        truth = -0.4
        traj = model.rollout_mean_field(
            initial_m=initial_m,
            steps=50,
            exogenous_truth=truth,
            temporal_asymmetry=0.6,
        )
        final_m = float(traj[-1])

        paradox = model.classify_paradox(initial_m=initial_m, final_m=final_m, exogenous_truth=truth)

        self.assertGreater(final_m, 0.2)
        self.assertTrue(paradox["self_fulfilling"])
        self.assertFalse(paradox["self_defeating"])

    def test_negative_temporal_lead_can_create_self_defeating_regime(self):
        params = HyperstitionParameters(
            narrative_inertia=0.3,
            social_coupling=0.0,
            observation_gain=1.4,
            observer_coupling=0.9,
            action_gain=2.5,
            temporal_bias_gain=3.0,
            noise_std=0.0,
        )
        model = HyperstitionToyModel(params=params)

        initial_m = 0.6
        truth = 0.4
        traj = model.rollout_mean_field(
            initial_m=initial_m,
            steps=50,
            exogenous_truth=truth,
            temporal_asymmetry=-0.6,
        )
        final_m = float(traj[-1])

        paradox = model.classify_paradox(initial_m=initial_m, final_m=final_m, exogenous_truth=truth)

        self.assertLess(final_m, -0.2)
        self.assertTrue(paradox["self_defeating"])
        self.assertFalse(paradox["self_fulfilling"])


if __name__ == "__main__":
    unittest.main()
