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


if __name__ == "__main__":
    unittest.main()
