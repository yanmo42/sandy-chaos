import unittest
import numpy as np

from nfem_suite.simulation.communication import VortexChannel


class TestFrameAsymmetryFalsification(unittest.TestCase):
    def _run_bidirectional_trial(self, channel: VortexChannel, steps: int = 80, dt: float = 0.1) -> dict:
        channel.set_source_a(np.array([3.0, 0.0]))
        channel.set_receiver_b(np.array([-3.0, 0.0]))

        t = 0.0
        for i in range(steps):
            # Synchronous bounded signal injection from both ends.
            # This keeps the comparison causal and symmetric at the source.
            signal = float(np.sin(0.2 * i) + 0.5 * np.cos(0.13 * i))
            channel.inject_signal_at_a(signal, t)
            channel.inject_signal_at_b(signal, t)
            t += dt
            channel.update(t)

        return channel.get_statistics()

    def test_null_model_stays_near_unit_asymmetry_ratio(self):
        null_channel = VortexChannel(
            vortex_center=np.array([0.0, 0.0]),
            vortex_radius=10.0,
            coupling_strength=1.0,
            backward_attenuation=1.0,
        )
        stats = self._run_bidirectional_trial(null_channel)

        # Null hypothesis: with symmetric attenuation and equal source drives,
        # forward and backward totals should be approximately equal.
        self.assertAlmostEqual(stats["asymmetry_ratio"], 1.0, delta=0.05)

    def test_coupled_model_falsifies_null_unit_asymmetry(self):
        coupled_channel = VortexChannel(
            vortex_center=np.array([0.0, 0.0]),
            vortex_radius=10.0,
            coupling_strength=1.0,
            backward_attenuation=0.5,
        )
        stats = self._run_bidirectional_trial(coupled_channel)

        # Coupled-model prediction under identical source drives:
        # backward total is attenuated vs forward by configured factor.
        self.assertAlmostEqual(stats["asymmetry_ratio"], 0.5, delta=0.05)

        # Falsification check: observed coupled ratio must contradict
        # the null expectation of ~1.0 by a meaningful margin.
        self.assertGreater(abs(stats["asymmetry_ratio"] - 1.0), 0.45)


if __name__ == "__main__":
    unittest.main()
