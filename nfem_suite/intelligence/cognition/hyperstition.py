"""Hyperstition toy dynamics.

This module provides a concrete toy specification for the open narrative update
law from docs/05:

    N_{t+1} = G(N_t, O_t, A_t, xi_t)

Model assumptions (minimal, explicit):
- Two-agent / two-narrative polarity is represented by scalar narrative state
  m in [-1, 1], where sign(m) selects narrative branch and |m| is commitment.
- Cross-temporal-frame communication enters as a bounded temporal asymmetry
  bias (delta_tau-like signal) in the action channel.
- Updates are strictly forward-causal in simulation time.

The code includes:
1) mean-field map + derivative for fixed-point analysis,
2) two-agent rollout dynamics,
3) paradox classifiers (self-fulfilling / self-defeating narrative regimes).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np


@dataclass
class HyperstitionParameters:
    """Parameters for the toy hyperstition dynamics.

    Attributes:
        narrative_inertia: Persistence of prior narrative commitment.
        social_coupling: Coupling to the group narrative mean.
        observation_gain: Weight on observation-driven update term.
        observer_coupling: Mix between exogenous truth and endogenous action feedback.
        action_gain: Sensitivity of action channel to narrative state.
        temporal_bias_gain: Strength of cross-temporal asymmetry bias in action channel.
        noise_std: Std dev for additive Gaussian process noise xi_t.
    """

    narrative_inertia: float = 0.9
    social_coupling: float = 0.2
    observation_gain: float = 1.0
    observer_coupling: float = 0.6
    action_gain: float = 2.0
    temporal_bias_gain: float = 1.0
    noise_std: float = 0.0


@dataclass
class FixedPoint:
    """Fixed-point result for the mean-field map."""

    value: float
    derivative: float
    stable: bool


class HyperstitionToyModel:
    """Concrete toy model for narrative-boundary dynamics G.

    Mean-field map:

        m_{t+1} = tanh((a + k)m_t + b[(1-r)T + r*tanh(g(m_t + h*Delta))])

    where:
        - m_t in [-1, 1] is narrative polarization,
        - T is exogenous truth signal,
        - Delta is temporal asymmetry (cross-frame communication leverage),
        - a, k, b, r, g, h correspond to parameter fields.
    """

    def __init__(self, params: Optional[HyperstitionParameters] = None, rng_seed: Optional[int] = None):
        self.params = params or HyperstitionParameters()
        self._rng = np.random.default_rng(rng_seed)

    @staticmethod
    def _sech2(x: float) -> float:
        c = np.cosh(x)
        return float(1.0 / (c * c))

    def mean_field_map(self, m: float, exogenous_truth: float = 0.0, temporal_asymmetry: float = 0.0) -> float:
        """Forward mean-field narrative update m_{t+1} = f(m_t)."""
        p = self.params
        temporal_shift = p.temporal_bias_gain * temporal_asymmetry
        action = np.tanh(p.action_gain * (m + temporal_shift))
        observation = (1.0 - p.observer_coupling) * exogenous_truth + p.observer_coupling * action
        inner = (p.narrative_inertia + p.social_coupling) * m + p.observation_gain * observation
        return float(np.tanh(inner))

    def mean_field_derivative(self, m: float, exogenous_truth: float = 0.0, temporal_asymmetry: float = 0.0) -> float:
        """Analytic derivative df/dm used for stability checks."""
        p = self.params
        temporal_shift = p.temporal_bias_gain * temporal_asymmetry
        action_inner = p.action_gain * (m + temporal_shift)
        action = np.tanh(action_inner)
        observation = (1.0 - p.observer_coupling) * exogenous_truth + p.observer_coupling * action
        inner = (p.narrative_inertia + p.social_coupling) * m + p.observation_gain * observation

        d_inner_dm = (
            (p.narrative_inertia + p.social_coupling)
            + p.observation_gain * p.observer_coupling * p.action_gain * self._sech2(action_inner)
        )
        return float(self._sech2(inner) * d_inner_dm)

    def rollout_mean_field(
        self,
        initial_m: float,
        steps: int = 80,
        exogenous_truth: float = 0.0,
        temporal_asymmetry: float = 0.0,
    ) -> np.ndarray:
        """Roll out mean-field dynamics for a single narrative coordinate."""
        p = self.params
        traj = np.zeros(steps + 1, dtype=float)
        traj[0] = float(np.clip(initial_m, -1.0, 1.0))

        for t in range(steps):
            nxt = self.mean_field_map(traj[t], exogenous_truth=exogenous_truth, temporal_asymmetry=temporal_asymmetry)
            if p.noise_std > 0.0:
                nxt += float(self._rng.normal(0.0, p.noise_std))
            traj[t + 1] = float(np.clip(nxt, -1.0, 1.0))

        return traj

    def simulate_two_agent(
        self,
        initial_state: np.ndarray,
        temporal_asymmetry: np.ndarray,
        exogenous_truth: float = 0.0,
        steps: int = 80,
    ) -> np.ndarray:
        """Simulate explicit two-agent coupled narrative dynamics.

        Args:
            initial_state: shape (2,), narrative coordinates in [-1, 1].
            temporal_asymmetry: shape (2,), per-agent cross-frame asymmetry bias.
            exogenous_truth: scalar truth signal in [-1, 1].
            steps: number of update steps.
        """
        p = self.params
        state = np.asarray(initial_state, dtype=float)
        bias = np.asarray(temporal_asymmetry, dtype=float)

        if state.shape != (2,):
            raise ValueError("initial_state must have shape (2,)")
        if bias.shape != (2,):
            raise ValueError("temporal_asymmetry must have shape (2,)")

        history = np.zeros((steps + 1, 2), dtype=float)
        history[0] = np.clip(state, -1.0, 1.0)

        for t in range(steps):
            current = history[t]
            actions = np.tanh(p.action_gain * (current + p.temporal_bias_gain * bias))
            mean_action = float(np.mean(actions))
            observation = (1.0 - p.observer_coupling) * exogenous_truth + p.observer_coupling * mean_action
            social_mean = float(np.mean(current))

            nxt = np.tanh(
                p.narrative_inertia * current
                + p.social_coupling * social_mean
                + p.observation_gain * observation
            )
            if p.noise_std > 0.0:
                nxt = nxt + self._rng.normal(0.0, p.noise_std, size=2)

            history[t + 1] = np.clip(nxt, -1.0, 1.0)

        return history

    def find_fixed_points(
        self,
        exogenous_truth: float = 0.0,
        temporal_asymmetry: float = 0.0,
        grid_points: int = 2001,
        tol: float = 1e-8,
        max_iter: int = 100,
    ) -> List[FixedPoint]:
        """Find fixed points of the mean-field map on [-1, 1] and classify stability."""

        def residual(x: float) -> float:
            return self.mean_field_map(x, exogenous_truth=exogenous_truth, temporal_asymmetry=temporal_asymmetry) - x

        def bisect(a: float, b: float) -> float:
            fa = residual(a)
            fb = residual(b)
            if abs(fa) <= tol:
                return float(a)
            if abs(fb) <= tol:
                return float(b)
            for _ in range(max_iter):
                m = 0.5 * (a + b)
                fm = residual(m)
                if abs(fm) <= tol or abs(b - a) <= tol:
                    return float(m)
                if fa * fm <= 0.0:
                    b, fb = m, fm
                else:
                    a, fa = m, fm
            return float(0.5 * (a + b))

        xs = np.linspace(-1.0, 1.0, int(grid_points))
        rs = np.array([residual(float(x)) for x in xs], dtype=float)

        roots: List[float] = []

        for i in range(len(xs) - 1):
            x0, x1 = float(xs[i]), float(xs[i + 1])
            r0, r1 = float(rs[i]), float(rs[i + 1])

            if abs(r0) <= tol:
                roots.append(x0)
            if r0 * r1 < 0.0:
                roots.append(bisect(x0, x1))

        if abs(float(rs[-1])) <= tol:
            roots.append(float(xs[-1]))

        unique: List[float] = []
        for r in sorted(roots):
            if not unique or abs(r - unique[-1]) > 1e-4:
                unique.append(r)

        fixed_points: List[FixedPoint] = []
        for r in unique:
            d = self.mean_field_derivative(r, exogenous_truth=exogenous_truth, temporal_asymmetry=temporal_asymmetry)
            fixed_points.append(FixedPoint(value=float(r), derivative=float(d), stable=abs(d) < 1.0))

        return fixed_points

    @staticmethod
    def classify_paradox(initial_m: float, final_m: float, exogenous_truth: float) -> Dict[str, bool]:
        """Classify trajectory-level narrative paradox signatures.

        Definitions:
        - self_fulfilling: final sign tracks initial sign while opposing truth sign.
        - self_defeating: initial sign matches truth sign, but final sign flips opposite.
        """
        init_sign = int(np.sign(initial_m))
        final_sign = int(np.sign(final_m))
        truth_sign = int(np.sign(exogenous_truth))

        self_fulfilling = (
            truth_sign != 0
            and final_sign != 0
            and init_sign == final_sign
            and final_sign != truth_sign
        )
        self_defeating = (
            truth_sign != 0
            and init_sign == truth_sign
            and final_sign == -truth_sign
        )

        return {
            "self_fulfilling": bool(self_fulfilling),
            "self_defeating": bool(self_defeating),
        }
