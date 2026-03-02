import unittest
import numpy as np

from nfem_suite.simulation.communication import VortexChannel


class TestTemporalFrameMetrics(unittest.TestCase):
    def test_directional_profiles_and_asymmetry_surface(self):
        channel = VortexChannel(
            vortex_center=np.array([0.0, 0.0]),
            vortex_radius=10.0,
            coupling_strength=2.0,
        )
        channel.set_source_a(np.array([-2.0, 0.0]))
        channel.set_receiver_b(np.array([2.0, 0.0]))

        # Causal transmissions only (received_time > sent_time).
        channel.forward_transmission_history.append(
            {'sent_time': 0.0, 'received_time': 0.4, 'delay': 0.4, 'signal': 1.0}
        )
        channel.forward_transmission_history.append(
            {'sent_time': 1.0, 'received_time': 1.8, 'delay': 0.8, 'signal': 2.0}
        )
        channel.backward_transmission_history.append(
            {'sent_time': 0.0, 'received_time': 0.6, 'delay': 0.6, 'signal': 0.5}
        )

        bins = np.array([0.0, 0.5, 1.0])
        metrics = channel.compute_temporal_frame_metrics(
            delta_tau_bins=bins,
            coupling_values=[1.0, 2.0],
        )

        self.assertEqual(metrics['C_A_to_B'].shape, (2,))
        self.assertEqual(metrics['C_B_to_A'].shape, (2,))
        self.assertTrue(np.allclose(metrics['C_A_to_B'], np.array([1.0, 2.0])))
        self.assertTrue(np.allclose(metrics['C_B_to_A'], np.array([0.0, 0.5])))
        self.assertTrue(np.allclose(metrics['asymmetry'], np.array([1.0, 1.5])))

        expected_surface = np.array([
            [0.5, 0.75],  # λ = 1.0 scales by 1/2
            [1.0, 1.5],   # λ = 2.0 matches baseline
        ])
        self.assertTrue(np.allclose(metrics['asymmetry_surface'], expected_surface))

    def test_noncausal_packets_are_ignored(self):
        channel = VortexChannel(vortex_center=np.array([0.0, 0.0]), vortex_radius=5.0)

        channel.forward_transmission_history.append(
            {'sent_time': 3.0, 'received_time': 3.0, 'delay': 0.0, 'signal': 10.0}
        )
        channel.backward_transmission_history.append(
            {'sent_time': 4.0, 'received_time': 3.9, 'delay': -0.1, 'signal': 10.0}
        )

        metrics = channel.compute_temporal_frame_metrics(delta_tau_bins=[0.0, 1.0])
        self.assertTrue(np.allclose(metrics['C_A_to_B'], np.array([0.0])))
        self.assertTrue(np.allclose(metrics['C_B_to_A'], np.array([0.0])))
        self.assertTrue(np.allclose(metrics['asymmetry'], np.array([0.0])))


if __name__ == '__main__':
    unittest.main()
