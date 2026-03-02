import unittest
import numpy as np

from nfem_suite.simulation.agents import ObserverCoupling, ObserverCouplingConfig


class TestObserverCoupling(unittest.TestCase):
    def setUp(self):
        self.positions = np.array([
            [30.0, 50.0],
            [35.0, 50.0],
            [70.0, 50.0],
            [75.0, 50.0],
        ])
        self.velocities = np.array([
            [1.0, 0.0],
            [0.8, 0.0],
            [-1.0, 0.0],
            [-0.7, 0.0],
        ])
        self.observer_states = {
            "A": {
                "probe_position": np.array([30.0, 50.0]),
                "probe_axis": np.array([1.0, 0.0]),
                "read_gain": 1.0,
                "write_gain": 1.0,
                "feedback": 0.3,
            },
            "B": {
                "probe_position": np.array([70.0, 50.0]),
                "probe_axis": np.array([-1.0, 0.0]),
                "read_gain": 1.0,
                "write_gain": 1.0,
                "feedback": -0.2,
            },
        }

    def test_disabled_coupling_returns_zero(self):
        coupling = ObserverCoupling(ObserverCouplingConfig(enabled=False))
        phi = coupling.perturbation_for_node(np.array([50.0, 50.0]), self.observer_states)
        self.assertTrue(np.allclose(phi, np.zeros(2)))

    def test_nonzero_coupling_is_bounded(self):
        coupling = ObserverCoupling(
            ObserverCouplingConfig(enabled=True, gain=0.5, probe_sigma=10.0, max_perturbation=0.4)
        )
        coupling.update_measurements(self.observer_states, self.positions, self.velocities)
        phi = coupling.perturbation_for_node(np.array([52.0, 50.0]), self.observer_states)

        self.assertGreater(np.linalg.norm(phi), 0.0)
        self.assertLessEqual(np.linalg.norm(phi), 0.4 + 1e-9)

    def test_gain_scaling_increases_effect(self):
        low = ObserverCoupling(ObserverCouplingConfig(enabled=True, gain=0.05, probe_sigma=12.0, max_perturbation=10.0))
        high = ObserverCoupling(ObserverCouplingConfig(enabled=True, gain=0.2, probe_sigma=12.0, max_perturbation=10.0))

        low.update_measurements(self.observer_states, self.positions, self.velocities)
        high.update_measurements(self.observer_states, self.positions, self.velocities)

        p = np.array([50.0, 50.0])
        phi_low = low.perturbation_for_node(p, self.observer_states)
        phi_high = high.perturbation_for_node(p, self.observer_states)

        self.assertGreater(np.linalg.norm(phi_high), np.linalg.norm(phi_low))

    def test_agency_observables_present_and_bounded(self):
        coupling = ObserverCoupling(
            ObserverCouplingConfig(enabled=True, gain=0.5, probe_sigma=10.0, decay=0.8, max_perturbation=1.0)
        )
        states = {
            "A": {**self.observer_states["A"], "temporal_frame_scale": 1.0},
            "B": {**self.observer_states["B"], "temporal_frame_scale": 2.0},
        }

        coupling.update_measurements(states, self.positions, self.velocities)
        _ = coupling.perturbation_for_node(np.array([52.0, 50.0]), states)
        stats = coupling.collect_step_stats([0.1, 0.2, 0.3], len(states))

        self.assertIn("intervention_gain", stats)
        self.assertIn("counterfactual_control_score", stats)
        self.assertIn("predictive_horizon", stats)
        self.assertGreaterEqual(stats["intervention_gain"], 0.0)
        self.assertLessEqual(stats["intervention_gain"], 1.0)
        self.assertGreaterEqual(stats["counterfactual_control_score"], 0.0)
        self.assertLessEqual(stats["counterfactual_control_score"], 1.0)
        self.assertGreater(stats["predictive_horizon"], 0.0)

    def test_counterfactual_control_increases_with_write_feedback(self):
        coupling_low = ObserverCoupling(ObserverCouplingConfig(enabled=True, decay=0.7))
        coupling_high = ObserverCoupling(ObserverCouplingConfig(enabled=True, decay=0.7))

        low_states = {
            "A": {**self.observer_states["A"], "feedback": 0.01},
            "B": {**self.observer_states["B"], "feedback": -0.01},
        }
        high_states = {
            "A": {**self.observer_states["A"], "feedback": 0.8},
            "B": {**self.observer_states["B"], "feedback": -0.8},
        }

        coupling_low.update_measurements(low_states, self.positions, self.velocities)
        coupling_high.update_measurements(high_states, self.positions, self.velocities)

        low_stats = coupling_low.collect_step_stats([0.1], len(low_states))
        high_stats = coupling_high.collect_step_stats([0.1], len(high_states))

        self.assertGreater(
            high_stats["counterfactual_control_score"],
            low_stats["counterfactual_control_score"],
        )


if __name__ == "__main__":
    unittest.main()
