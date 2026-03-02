"""Read-write observer coupling model.

Implements a concrete feedback term Φ(S_t, M_t, feedback) that perturbs local
flow as a bounded, localized backreaction field around observer probe points.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import numpy as np


@dataclass
class ObserverCouplingConfig:
    """Configuration for observer read-write coupling.

    Attributes:
        enabled: Master switch for the coupling term.
        gain: Global scaling factor λ for the coupling contribution.
        probe_sigma: Spatial footprint (std dev) of each observer probe.
        decay: Temporal smoothing of measurement memory (0..1).
        max_perturbation: Hard bound for perturbation vector magnitude.
    """

    enabled: bool = True
    gain: float = 0.15
    probe_sigma: float = 8.0
    decay: float = 0.9
    max_perturbation: float = 2.0


class ObserverCoupling:
    """Concrete implementation of Φ(S_t, M_t, feedback).

    The perturbation field is computed as:

        Φ(x, t) = Σ_i λ * G_i(x) * [r_i * m_i(t) + w_i * f_i(t)] * u_i(x)

    where:
        - G_i(x): Gaussian spatial kernel around observer probe i
        - m_i(t): exponentially smoothed local measurement at probe i (read)
        - f_i(t): feedback scalar derived from observer state S_t (write)
        - r_i, w_i: per-observer read/write gains
        - u_i(x): radial unit vector from probe to x

    This is fully forward-causal in simulation time: measurements and feedback are
    computed from current state only, then applied to the next physics update.
    """

    def __init__(self, config: ObserverCouplingConfig):
        self.config = config
        self._measurement_memory: Dict[str, float] = {}
        self._observer_activity: Dict[str, Dict[str, float]] = {}
        self._last_stats: Dict[str, float] = {
            "mean_perturbation": 0.0,
            "max_perturbation": 0.0,
            "active_observers": 0.0,
            "intervention_gain": 0.0,
            "counterfactual_control_score": 0.0,
            "predictive_horizon": 0.0,
        }

    @staticmethod
    def _gaussian_weight(distance: float, sigma: float) -> float:
        return float(np.exp(-(distance ** 2) / (2.0 * sigma ** 2)))

    @staticmethod
    def _safe_unit(vec: np.ndarray, eps: float = 1e-8) -> np.ndarray:
        n = float(np.linalg.norm(vec))
        if n < eps:
            return np.array([1.0, 0.0], dtype=float)
        return vec / n

    def update_measurements(self, observer_states: Dict[str, Dict[str, Any]],
                            positions: np.ndarray,
                            velocities: np.ndarray) -> None:
        """Update smoothed measurements m_i(t) from local probe neighborhoods."""
        if positions.size == 0 or velocities.size == 0:
            return

        activity: Dict[str, Dict[str, float]] = {}

        for name, state in observer_states.items():
            probe = np.asarray(state["probe_position"], dtype=float)
            deltas = positions - probe
            dists = np.linalg.norm(deltas, axis=1)
            kernel = np.exp(-(dists ** 2) / (2.0 * self.config.probe_sigma ** 2))
            wsum = float(kernel.sum())

            if wsum <= 1e-9:
                measurement = 0.0
            else:
                local_v = (velocities * kernel[:, None]).sum(axis=0) / wsum
                axis = self._safe_unit(np.asarray(state.get("probe_axis", [1.0, 0.0]), dtype=float))
                measurement = float(np.dot(local_v, axis))

            prev = self._measurement_memory.get(name, measurement)
            smooth = self.config.decay * prev + (1.0 - self.config.decay) * measurement
            self._measurement_memory[name] = float(smooth)

            read_gain = float(state.get("read_gain", 1.0))
            write_gain = float(state.get("write_gain", 1.0))
            feedback = float(state.get("feedback", 0.0))
            frame_scale = float(state.get("temporal_frame_scale", 1.0))

            read_term = read_gain * float(smooth)
            write_term = write_gain * feedback

            activity[name] = {
                "read_term": read_term,
                "write_term": write_term,
                "full_drive": read_term + write_term,
                "frame_scale": max(0.0, frame_scale),
            }

        self._observer_activity = activity

    def perturbation_for_node(self, node_position: np.ndarray,
                              observer_states: Dict[str, Dict[str, Any]]) -> np.ndarray:
        """Compute coupling perturbation at a node position."""
        if not self.config.enabled or not observer_states:
            return np.zeros(2, dtype=float)

        phi = np.zeros(2, dtype=float)

        for name, state in observer_states.items():
            probe = np.asarray(state["probe_position"], dtype=float)
            delta = np.asarray(node_position, dtype=float) - probe
            dist = float(np.linalg.norm(delta))
            kernel = self._gaussian_weight(dist, self.config.probe_sigma)

            read_gain = float(state.get("read_gain", 1.0))
            write_gain = float(state.get("write_gain", 1.0))

            measurement = float(self._measurement_memory.get(name, 0.0))
            feedback = float(state.get("feedback", 0.0))
            source_strength = self.config.gain * (read_gain * measurement + write_gain * feedback)

            direction = self._safe_unit(delta)
            phi += kernel * source_strength * direction

        mag = float(np.linalg.norm(phi))
        if mag > self.config.max_perturbation:
            phi = phi / mag * self.config.max_perturbation

        return phi

    def collect_step_stats(self, perturbation_magnitudes: list[float], observer_count: int) -> Dict[str, float]:
        if perturbation_magnitudes:
            mean_p = float(np.mean(perturbation_magnitudes))
            max_p = float(np.max(perturbation_magnitudes))
        else:
            mean_p = 0.0
            max_p = 0.0

        if self._observer_activity:
            drives = list(self._observer_activity.values())

            # Fraction of available perturbation budget currently being used.
            # This is tied to realized perturbation (not latent drive terms),
            # keeping the observable grounded in forward-applied actuation.
            intervention_gain = float(
                np.clip(
                    mean_p / max(self.config.max_perturbation, 1e-9),
                    0.0,
                    1.0,
                )
            )

            # Write-channel share of total local control effort.
            # Using |read| + |write| avoids cancellation artifacts and preserves
            # a strictly present-step decomposition of control allocation.
            control_ratios = [
                abs(v["write_term"]) / (abs(v["read_term"]) + abs(v["write_term"]) + 1e-9)
                for v in drives
            ]
            counterfactual_control_score = float(np.clip(np.mean(control_ratios), 0.0, 1.0))

            # Predictive horizon proxy in effective future update steps.
            # Larger smoothing memory and larger frame-scale imply longer
            # forward-looking persistence of actionable signal.
            memory_steps = 1.0 / max(1.0 - min(self.config.decay, 0.999), 1e-3)
            mean_frame_scale = float(np.mean([v["frame_scale"] for v in drives]))
            predictive_horizon = float(memory_steps * mean_frame_scale)
        else:
            intervention_gain = 0.0
            counterfactual_control_score = 0.0
            predictive_horizon = 0.0

        self._last_stats = {
            "mean_perturbation": mean_p,
            "max_perturbation": max_p,
            "active_observers": float(observer_count),
            "intervention_gain": intervention_gain,
            "counterfactual_control_score": counterfactual_control_score,
            "predictive_horizon": predictive_horizon,
        }
        return self._last_stats

    def diagnostics(self) -> Dict[str, float]:
        return dict(self._last_stats)
