import unittest

import matplotlib

matplotlib.use("Agg")

from nfem_suite.visualization.dashboard import Dashboard


class TestDashboardTraces(unittest.TestCase):
    def test_records_observer_drift_and_frame_asymmetry(self):
        dashboard = Dashboard(mode="full")

        dashboard._record_dashboard_traces(
            time=0.0,
            observer_coupling_stats={"mean_perturbation": 0.2},
            temporal_frame_metrics={"asymmetry": [0.5, -0.25]},
        )
        dashboard._record_dashboard_traces(
            time=1.0,
            observer_coupling_stats={"mean_perturbation": 0.5},
            temporal_frame_metrics={"asymmetry": [0.1, -0.2, 0.3]},
        )

        self.assertEqual(dashboard.trace_time_history, [0.0, 1.0])
        self.assertEqual(dashboard.observer_coupling_drift_history[0], 0.0)
        self.assertAlmostEqual(dashboard.observer_coupling_drift_history[1], 0.3, places=9)
        self.assertAlmostEqual(dashboard.frame_channel_asymmetry_history[0], 0.75, places=9)
        self.assertAlmostEqual(dashboard.frame_channel_asymmetry_history[1], 0.6, places=9)


if __name__ == "__main__":
    unittest.main()
