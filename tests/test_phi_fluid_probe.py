import unittest

from nfem_suite.simulation.agents.observer_coupling import ObserverCouplingConfig
from nfem_suite.simulation.flows import SPDDConfig, make_grid, run_spdd


class PhiFluidProbeTests(unittest.TestCase):
    def test_make_grid_is_deterministic_shape(self):
        grid = make_grid(rows=2, cols=3, width=10.0, height=4.0)
        self.assertEqual(grid.shape, (6, 2))
        self.assertEqual(grid[0].tolist(), [0.0, 0.0])
        self.assertEqual(grid[-1].tolist(), [10.0, 4.0])

    def test_spdd_probe_deflects_downstream_but_stays_bounded(self):
        cfg = SPDDConfig(
            observer=ObserverCouplingConfig(gain=0.3, probe_sigma=8.0, max_perturbation=0.2),
        )
        run = run_spdd(cfg)

        self.assertTrue(run.bounded)
        self.assertLessEqual(run.max_perturbation, cfg.observer.max_perturbation + cfg.noise_floor)
        self.assertGreater(run.max_downstream_deflection, cfg.noise_floor)
        self.assertTrue(any(v > cfg.noise_floor for v in run.deflection_by_distance.values()))

    def test_zero_gain_is_noise_floor_null_case(self):
        run = run_spdd(SPDDConfig(observer=ObserverCouplingConfig(gain=0.0)))

        self.assertEqual(run.max_perturbation, 0.0)
        self.assertEqual(run.max_downstream_deflection, 0.0)
        self.assertTrue(run.bounded)

    def test_spdd_run_is_reproducible(self):
        cfg = SPDDConfig(observer=ObserverCouplingConfig(gain=0.15, probe_sigma=7.0, max_perturbation=0.5))
        first = run_spdd(cfg).to_dict()
        second = run_spdd(cfg).to_dict()

        self.assertEqual(first["deflection_by_distance"], second["deflection_by_distance"])
        self.assertEqual(first["max_perturbation"], second["max_perturbation"])


if __name__ == "__main__":
    unittest.main()
