"""
Simulation Universe Module
==========================
Manages the cosmic simulation: black hole, perturbations, and photon tracing.
"""

import numpy as np
from collections import Counter
from typing import List, Dict, Optional

from cosmic_comm.physics.metric import KerrBlackHole
from cosmic_comm.physics.geodesics import GeodesicTracer
from cosmic_comm.physics.perturbation import MassPerturbation

class CosmicUniverse:
    def __init__(
        self,
        M: float = 1.0,
        a: float = 0.9,
        step_size: float = 0.05,
        max_steps: int = 1500,
        null_tolerance: float = 1e-2,
        max_radius_factor: float = 50.0,
        capture_margin: float = 1.05,
        perturb_force_scale: float = 100.0,
        perturb_softening: float = 0.1
    ):
        # Spacetime
        self.black_hole = KerrBlackHole(M, a)

        # Integration defaults
        self.default_max_steps = int(max_steps)

        # Perturbation defaults
        self.perturb_force_scale = float(perturb_force_scale)
        self.perturb_softening = float(perturb_softening)
        
        # Perturbations (Obstacles)
        self.perturbations: List[MassPerturbation] = []
        
        # Physics Engine
        self.tracer = GeodesicTracer(
            self.black_hole,
            step_size=step_size,
            perturbations=self.perturbations,
            null_tolerance=null_tolerance,
            max_radius_factor=max_radius_factor,
            capture_margin=capture_margin,
        )
        
    def add_perturbation(
        self,
        r: float,
        theta: float,
        phi: float,
        mass: float = 0.1,
        force_scale: Optional[float] = None,
        softening: Optional[float] = None,
    ):
        """Add a mass to the universe."""
        p = MassPerturbation(
            r,
            theta,
            phi,
            mass,
            force_scale=self.perturb_force_scale if force_scale is None else force_scale,
            softening=self.perturb_softening if softening is None else softening,
        )
        self.perturbations.append(p)
        # Update tracer reference (though list is mutable, good to be safe)
        self.tracer.perturbations = self.perturbations
        print(f"Added perturbation at r={r:.1f}, phi={phi:.1f}, mass={mass}")
        
    def clear_perturbations(self):
        self.perturbations.clear()
        
    def _initialize_parallel_ray(
        self,
        start_x: float,
        y: float,
        theta: float = np.pi / 2.0,
        energy: float = 1.0,
    ) -> Optional[np.ndarray]:
        """Initialize a ray approximately parallel to the x-axis at x=start_x."""
        r = float(np.sqrt(start_x**2 + y**2))
        phi = float(np.arctan2(y, start_x))

        # Initial momenta (approximate for parallel beam)
        pt = -abs(float(energy))
        pphi = float(y)
        ptheta = 0.0

        g_inv = self.black_hole.inverse_metric_components(r, theta)

        B = (
            g_inv['tt'] * pt**2 +
            2 * g_inv['tphi'] * pt * pphi +
            g_inv['thth'] * ptheta**2 +
            g_inv['phiphi'] * pphi**2
        )
        A = g_inv['rr']

        if abs(A) < 1e-12:
            return None

        pr_sq = -B / A
        if pr_sq < -1e-10:
            return None

        pr = -np.sqrt(max(pr_sq, 0.0))
        return np.array([0.0, r, theta, phi, pt, pr, ptheta, pphi], dtype=float)

    def run_beam_simulation(
        self,
        start_x: float = 20.0,
        width: float = 20.0,
        rays: int = 40,
        max_steps: Optional[int] = None,
        theta: float = np.pi / 2.0,
        energy: float = 1.0,
    ):
        """
        Run a simulation of a parallel beam of photons.
        Returns a list of trajectory dictionaries.
        """
        trajectories = []
        y_range = np.linspace(-width/2, width/2, rays)
        chosen_max_steps = self.default_max_steps if max_steps is None else int(max_steps)
        
        for ray_index, y in enumerate(y_range):
            state = self._initialize_parallel_ray(start_x=start_x, y=float(y), theta=theta, energy=energy)
            if state is None:
                continue

            traj = self.tracer.trace(state, max_steps=chosen_max_steps)
            traj['ray_index'] = int(ray_index)
            traj['initial_y'] = float(y)
            traj['initial_phi'] = float(state[3])
            trajectories.append(traj)
                
        return trajectories

    @staticmethod
    def _deflection_angle(traj: Dict) -> float:
        phi = traj.get('phi', np.array([]))
        if len(phi) == 0:
            return float('nan')
        initial_phi = float(traj.get('initial_phi', phi[0]))
        return float(phi[-1] - initial_phi)

    def summarize_trajectories(self, trajectories: List[Dict]) -> Dict[str, float]:
        """Aggregate status and trajectory quality metrics for a beam run."""
        total = len(trajectories)
        if total == 0:
            return {
                'total_rays': 0,
                'captured_fraction': 0.0,
                'escaped_fraction': 0.0,
                'max_steps_fraction': 0.0,
                'numerical_error_fraction': 0.0,
                'constraint_warning_fraction': 0.0,
                'constraint_violation_fraction': 0.0,
                'mean_abs_deflection': np.nan,
                'max_abs_deflection': np.nan,
                'mean_steps': np.nan,
                'mean_proper_time': np.nan,
                'mean_null_error': np.nan,
                'mean_final_null_error': np.nan,
                'max_null_error': np.nan,
            }

        status_counts = Counter(traj.get('status', 'unknown') for traj in trajectories)

        deflections = np.array([
            self._deflection_angle(traj) for traj in trajectories
        ], dtype=float)
        abs_deflections = np.abs(deflections[np.isfinite(deflections)])

        steps = np.array([traj.get('steps', np.nan) for traj in trajectories], dtype=float)
        proper_times = np.array([traj.get('proper_time', np.nan) for traj in trajectories], dtype=float)
        mean_null_errors = np.array([traj.get('mean_null_error', np.nan) for traj in trajectories], dtype=float)
        final_null_errors = np.array([traj.get('final_null_error', np.nan) for traj in trajectories], dtype=float)
        max_null_errors = np.array([traj.get('max_null_error', np.nan) for traj in trajectories], dtype=float)
        constraint_violations = np.array([bool(traj.get('constraint_violated', False)) for traj in trajectories], dtype=bool)

        summary = {
            'total_rays': float(total),
            'captured_fraction': status_counts.get('captured', 0) / total,
            'escaped_fraction': status_counts.get('escaped', 0) / total,
            'max_steps_fraction': status_counts.get('max_steps', 0) / total,
            'numerical_error_fraction': status_counts.get('numerical_error', 0) / total,
            'constraint_warning_fraction': status_counts.get('constraint_warning', 0) / total,
            'constraint_violation_fraction': float(np.mean(constraint_violations)) if constraint_violations.size else 0.0,
            'mean_abs_deflection': float(np.nanmean(abs_deflections)) if abs_deflections.size else np.nan,
            'max_abs_deflection': float(np.nanmax(abs_deflections)) if abs_deflections.size else np.nan,
            'mean_signed_deflection': float(np.nanmean(deflections)) if deflections.size else np.nan,
            'mean_steps': float(np.nanmean(steps)) if steps.size else np.nan,
            'mean_proper_time': float(np.nanmean(proper_times)) if proper_times.size else np.nan,
            'mean_null_error': float(np.nanmean(mean_null_errors)) if mean_null_errors.size else np.nan,
            'mean_final_null_error': float(np.nanmean(final_null_errors)) if final_null_errors.size else np.nan,
            'max_null_error': float(np.nanmax(max_null_errors)) if max_null_errors.size else np.nan,
        }
        return summary

    def compare_trajectory_sets(self, baseline: List[Dict], perturbed: List[Dict]) -> Dict[str, float]:
        """Compare two beam runs ray-by-ray (matched by ray index)."""
        def ray_key(traj: Dict):
            return traj.get('ray_index', None)

        baseline_map = {ray_key(traj): traj for traj in baseline if ray_key(traj) is not None}
        perturbed_map = {ray_key(traj): traj for traj in perturbed if ray_key(traj) is not None}

        common_keys = sorted(set(baseline_map.keys()).intersection(perturbed_map.keys()))
        if len(common_keys) == 0:
            return {
                'common_rays': 0,
                'mean_delta_abs_deflection': np.nan,
                'max_delta_abs_deflection': np.nan,
                'captured_delta': np.nan,
                'escaped_delta': np.nan,
            }

        delta_abs_deflections = []
        for key in common_keys:
            d_base = abs(self._deflection_angle(baseline_map[key]))
            d_pert = abs(self._deflection_angle(perturbed_map[key]))
            if np.isfinite(d_base) and np.isfinite(d_pert):
                delta_abs_deflections.append(d_pert - d_base)

        summary_base = self.summarize_trajectories([baseline_map[k] for k in common_keys])
        summary_pert = self.summarize_trajectories([perturbed_map[k] for k in common_keys])

        delta_abs_deflections = np.array(delta_abs_deflections, dtype=float)
        return {
            'common_rays': float(len(common_keys)),
            'mean_delta_abs_deflection': float(np.nanmean(delta_abs_deflections)) if delta_abs_deflections.size else np.nan,
            'max_delta_abs_deflection': float(np.nanmax(np.abs(delta_abs_deflections))) if delta_abs_deflections.size else np.nan,
            'captured_delta': summary_pert['captured_fraction'] - summary_base['captured_fraction'],
            'escaped_delta': summary_pert['escaped_fraction'] - summary_base['escaped_fraction'],
        }
