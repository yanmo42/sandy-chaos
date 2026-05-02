"""Bounded Φ fluid-probe scenario (SPDD v0).

SPDD = single-probe downstream deflection. The scenario is deliberately small:
a uniform flow receives one localized observer-coupling perturbation and reports
whether downstream transverse velocity changes in a bounded, reproducible way.

This is a simulation probe, not evidence for any retrocausal or non-local
claim. The perturbation is applied forward in the current update only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from nfem_suite.simulation.agents.observer_coupling import ObserverCouplingConfig


@dataclass(frozen=True)
class SPDDConfig:
    """Configuration for the single-probe downstream deflection test."""

    grid_width: float = 100.0
    grid_height: float = 40.0
    rows: int = 5
    cols: int = 11
    base_speed: float = 1.0
    probe_position: tuple[float, float] = (20.0, 20.0)
    downstream_distances: tuple[float, ...] = (10.0, 20.0, 30.0, 40.0)
    downstream_band: float = 5.0
    longitudinal_decay: float = 35.0
    observer: ObserverCouplingConfig = field(default_factory=ObserverCouplingConfig)
    noise_floor: float = 1e-9


@dataclass(frozen=True)
class SPDDRun:
    """Result bundle for an SPDD v0 run."""

    config: SPDDConfig
    positions: np.ndarray
    baseline_velocities: np.ndarray
    perturbed_velocities: np.ndarray
    deflection_by_distance: dict[float, float]
    max_perturbation: float
    bounded: bool
    noise_floor: float

    @property
    def max_downstream_deflection(self) -> float:
        if not self.deflection_by_distance:
            return 0.0
        return max(self.deflection_by_distance.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": {
                "grid_width": self.config.grid_width,
                "grid_height": self.config.grid_height,
                "rows": self.config.rows,
                "cols": self.config.cols,
                "base_speed": self.config.base_speed,
                "probe_position": list(self.config.probe_position),
                "downstream_distances": list(self.config.downstream_distances),
                "observer_gain": self.config.observer.gain,
                "probe_sigma": self.config.observer.probe_sigma,
                "max_perturbation": self.config.observer.max_perturbation,
            },
            "node_count": int(len(self.positions)),
            "deflection_by_distance": {str(k): v for k, v in self.deflection_by_distance.items()},
            "max_perturbation": self.max_perturbation,
            "max_downstream_deflection": self.max_downstream_deflection,
            "bounded": self.bounded,
            "noise_floor": self.noise_floor,
        }


def make_grid(
    rows: int = 5,
    cols: int = 11,
    *,
    width: float = 100.0,
    height: float = 40.0,
) -> np.ndarray:
    """Return a deterministic 2D node grid as an ``(N, 2)`` array."""

    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive")
    xs = np.linspace(0.0, float(width), int(cols))
    ys = np.linspace(0.0, float(height), int(rows))
    return np.array([(x, y) for x in xs for y in ys], dtype=float)


def _bounded_transverse_perturbation(positions: np.ndarray, cfg: SPDDConfig) -> np.ndarray:
    """Compute a localized, forward-causal transverse perturbation field."""

    probe = np.asarray(cfg.probe_position, dtype=float)
    delta = positions - probe
    downstream = np.maximum(delta[:, 0], 0.0)
    lateral = delta[:, 1]

    sigma = max(float(cfg.observer.probe_sigma), 1e-9)
    longitudinal_scale = max(float(cfg.longitudinal_decay), 1e-9)
    lateral_profile = np.exp(-(lateral ** 2) / (2.0 * sigma ** 2))
    downstream_decay = np.exp(-downstream / longitudinal_scale)

    # The sign term makes the probe an observable deflector rather than a mere
    # speed boost. Nodes exactly on the probe centerline receive a tiny positive
    # transverse nudge so the centerline downstream observable is not masked by
    # symmetry in small grids.
    sign = np.sign(lateral)
    sign[sign == 0.0] = 1.0

    transverse = float(cfg.observer.gain) * lateral_profile * downstream_decay * sign
    transverse[delta[:, 0] < 0.0] = 0.0

    max_p = max(float(cfg.observer.max_perturbation), 0.0)
    if max_p > 0.0:
        transverse = np.clip(transverse, -max_p, max_p)
    return np.column_stack([np.zeros(len(positions), dtype=float), transverse])


def _downstream_deflection(
    positions: np.ndarray,
    baseline: np.ndarray,
    perturbed: np.ndarray,
    cfg: SPDDConfig,
) -> dict[float, float]:
    probe_x = float(cfg.probe_position[0])
    band = max(float(cfg.downstream_band), 1e-9)
    out: dict[float, float] = {}
    transverse_delta = np.abs(perturbed[:, 1] - baseline[:, 1])
    for dist in cfg.downstream_distances:
        target_x = probe_x + float(dist)
        mask = np.abs(positions[:, 0] - target_x) <= band
        if not bool(mask.any()):
            out[float(dist)] = 0.0
        else:
            out[float(dist)] = float(np.mean(transverse_delta[mask]))
    return out


def run_spdd(config: SPDDConfig | None = None) -> SPDDRun:
    """Run the bounded SPDD v0 scenario and return all observable surfaces."""

    cfg = config or SPDDConfig()
    positions = make_grid(cfg.rows, cfg.cols, width=cfg.grid_width, height=cfg.grid_height)
    baseline = np.column_stack([
        np.full(len(positions), float(cfg.base_speed), dtype=float),
        np.zeros(len(positions), dtype=float),
    ])
    perturbation = _bounded_transverse_perturbation(positions, cfg)
    perturbed = baseline + perturbation
    magnitudes = np.linalg.norm(perturbation, axis=1)
    max_mag = float(np.max(magnitudes)) if len(magnitudes) else 0.0
    deflection = _downstream_deflection(positions, baseline, perturbed, cfg)
    max_allowed = max(float(cfg.observer.max_perturbation), 0.0) + cfg.noise_floor

    return SPDDRun(
        config=cfg,
        positions=positions,
        baseline_velocities=baseline,
        perturbed_velocities=perturbed,
        deflection_by_distance=deflection,
        max_perturbation=max_mag,
        bounded=max_mag <= max_allowed,
        noise_floor=cfg.noise_floor,
    )
