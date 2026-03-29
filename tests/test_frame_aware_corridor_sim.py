import unittest

from scripts.frame_aware_corridor_sim import (
    CorridorSpec,
    SimulationConfig,
    compute_gamma_corridor,
    run_all_baselines,
)


class TestFrameAwareCorridorSim(unittest.TestCase):
    def setUp(self) -> None:
        self.corridor = CorridorSpec()

    def test_zero_delay_sanity_keeps_remote_baselines_aligned(self):
        config = SimulationConfig(
            propagation_delay_steps=0,
            clock_mismatch_s=0.0,
            validity_window_s=0.55,
        )

        results = run_all_baselines(self.corridor, config)
        naive = results["delay_ignorant_remote"]
        aware = results["frame_aware_corridor"]

        self.assertAlmostEqual(naive.gamma_corridor, aware.gamma_corridor, delta=1e-9)
        self.assertAlmostEqual(naive.violation_rate, aware.violation_rate, delta=1e-9)
        self.assertEqual(naive.packets_applied_stale, 0)
        self.assertEqual(aware.packets_rejected_expired, 0)

    def test_delay_ignorant_remote_degrades_with_higher_delay(self):
        low_delay = SimulationConfig(
            propagation_delay_steps=1,
            clock_mismatch_s=0.12,
            validity_window_s=0.55,
        )
        high_delay = SimulationConfig(
            propagation_delay_steps=6,
            clock_mismatch_s=0.12,
            validity_window_s=0.55,
        )

        low_results = run_all_baselines(self.corridor, low_delay)
        high_results = run_all_baselines(self.corridor, high_delay)

        low_naive = low_results["delay_ignorant_remote"]
        high_naive = high_results["delay_ignorant_remote"]

        self.assertGreater(low_naive.gamma_corridor, high_naive.gamma_corridor)
        self.assertLess(low_naive.violation_rate, high_naive.violation_rate)
        self.assertLess(low_naive.control_effort, high_naive.control_effort)
        self.assertGreater(high_naive.packets_applied_stale, 0)

    def test_frame_aware_controller_rejects_expired_packets(self):
        config = SimulationConfig(
            propagation_delay_steps=6,
            clock_mismatch_s=0.12,
            validity_window_s=0.30,
        )

        results = run_all_baselines(self.corridor, config)
        naive = results["delay_ignorant_remote"]
        aware = results["frame_aware_corridor"]
        local_only = results["local_only"]

        self.assertGreater(naive.packets_applied_stale, 0)
        self.assertEqual(aware.packets_applied_stale, 0)
        self.assertGreater(aware.packets_rejected_expired, 0)
        self.assertAlmostEqual(aware.gamma_corridor, local_only.gamma_corridor, delta=1e-9)
        self.assertAlmostEqual(aware.violation_rate, local_only.violation_rate, delta=1e-9)

    def test_frame_aware_controller_beats_delay_ignorant_remote_in_moderate_delay_regime(self):
        config = SimulationConfig(
            propagation_delay_steps=3,
            clock_mismatch_s=0.12,
            validity_window_s=0.55,
        )

        results = run_all_baselines(self.corridor, config)
        naive = results["delay_ignorant_remote"]
        aware = results["frame_aware_corridor"]

        self.assertGreater(aware.gamma_corridor, naive.gamma_corridor)
        self.assertLess(aware.violation_rate, naive.violation_rate)

    def test_gamma_corridor_scores_in_corridor_paths_above_off_corridor_paths(self):
        mostly_centered = [0.0, 0.1, -0.08, 0.12, -0.05]
        mostly_outside = [0.95, 1.2, -1.1, 1.4, -1.3]

        good_gamma = compute_gamma_corridor(mostly_centered, half_width=0.9)
        bad_gamma = compute_gamma_corridor(mostly_outside, half_width=0.9)

        self.assertGreater(good_gamma, bad_gamma)
        self.assertGreater(good_gamma, 0.85)
        self.assertLess(bad_gamma, 0.1)


if __name__ == "__main__":
    unittest.main()
