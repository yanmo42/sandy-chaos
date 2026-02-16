"""
Cosmic Communication Simulation
===============================
Simulates light bending and communication around a Kerr Black Hole.
Demonstrates how placing a perturbation (mass) alters the light paths.
"""

import json
import numpy as np
from dataclasses import dataclass

from cosmic_comm.simulation.universe import CosmicUniverse
from cosmic_comm.visualization.plotter import CosmicPlotter

@dataclass
class CosmicRunConfig:
    # Spacetime and integrator
    M: float = 1.0
    a: float = 0.9
    step_size: float = 0.05
    max_steps: int = 1500
    null_tolerance: float = 1e-2

    # Beam
    start_x: float = 20.0
    beam_width: float = 15.0
    rays: int = 30
    beam_theta: float = np.pi / 2.0
    beam_energy: float = 1.0

    # Perturbation (Observer A)
    perturb_r: float = 8.0
    perturb_theta: float = np.pi / 2.0
    perturb_phi: float = np.pi / 4
    perturb_mass: float = 0.5
    perturb_force_scale: float = 100.0
    perturb_softening: float = 0.1

    # Output
    output_path: str = 'cosmic_comm_demo.png'
    report_path: str = 'cosmic_comm_report.json'
    output_dpi: int = 180


def _format_summary_block(title: str, summary: dict) -> list:
    return [
        title,
        f"rays={int(summary['total_rays'])} cap={summary['captured_fraction']:.2f} esc={summary['escaped_fraction']:.2f}",
        f"|Δφ|mean={summary['mean_abs_deflection']:.3f} |Δφ|max={summary['max_abs_deflection']:.3f}",
        f"null_mean={summary['mean_null_error']:.2e} null_max={summary['max_null_error']:.2e}",
        f"constraint_violation={summary['constraint_violation_fraction']:.2f}",
    ]


def _print_summary(name: str, summary: dict):
    print(
        f"{name:<10} | rays={int(summary['total_rays']):3d} "
        f"capt={summary['captured_fraction']:.2f} esc={summary['escaped_fraction']:.2f} "
        f"|Δφ|mean={summary['mean_abs_deflection']:.3f} "
        f"null_max={summary['max_null_error']:.2e} "
        f"constraint_violation={summary['constraint_violation_fraction']:.2f}"
    )


def _print_comparison(comparison: dict):
    print(
        f"Comparison | common={int(comparison['common_rays']):3d} "
        f"Δ|Δφ|mean={comparison['mean_delta_abs_deflection']:.3f} "
        f"Δ|Δφ|max={comparison['max_delta_abs_deflection']:.3f} "
        f"Δcapt={comparison['captured_delta']:+.2f} "
        f"Δesc={comparison['escaped_delta']:+.2f}"
    )


def _deflection_angle(traj: dict) -> float:
    phi = traj.get('phi', np.array([]))
    if len(phi) == 0:
        return float('nan')
    initial_phi = float(traj.get('initial_phi', phi[0]))
    return float(phi[-1] - initial_phi)


def _compute_per_ray_delta_data(baseline: list, perturbed: list):
    """Return arrays for plotting plus structured per-ray comparison rows."""
    baseline_map = {traj.get('ray_index'): traj for traj in baseline if traj.get('ray_index') is not None}
    pert_map = {traj.get('ray_index'): traj for traj in perturbed if traj.get('ray_index') is not None}

    common_keys = sorted(set(baseline_map.keys()).intersection(pert_map.keys()))

    x_positions = []
    delta_abs = []
    rows = []

    for ray_idx in common_keys:
        b = baseline_map[ray_idx]
        p = pert_map[ray_idx]

        d_base = abs(_deflection_angle(b))
        d_pert = abs(_deflection_angle(p))
        delta = float(d_pert - d_base) if np.isfinite(d_base) and np.isfinite(d_pert) else float('nan')
        initial_y = float(p.get('initial_y', b.get('initial_y', np.nan)))

        if np.isfinite(initial_y) and np.isfinite(delta):
            x_positions.append(initial_y)
            delta_abs.append(delta)

        rows.append({
            'ray_index': int(ray_idx),
            'initial_y': initial_y,
            'baseline_status': str(b.get('status', 'unknown')),
            'perturbed_status': str(p.get('status', 'unknown')),
            'baseline_abs_deflection': float(d_base) if np.isfinite(d_base) else float('nan'),
            'perturbed_abs_deflection': float(d_pert) if np.isfinite(d_pert) else float('nan'),
            'delta_abs_deflection': float(delta) if np.isfinite(delta) else float('nan'),
        })

    return np.array(x_positions, dtype=float), np.array(delta_abs, dtype=float), rows


def _sanitize_for_json(value):
    """Convert numpy/scientific values to strict JSON-safe values."""
    if isinstance(value, dict):
        return {str(k): _sanitize_for_json(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_sanitize_for_json(v) for v in value]

    if isinstance(value, tuple):
        return [_sanitize_for_json(v) for v in value]

    if isinstance(value, np.ndarray):
        return [_sanitize_for_json(v) for v in value.tolist()]

    if isinstance(value, np.generic):
        return _sanitize_for_json(value.item())

    if isinstance(value, float):
        return value if np.isfinite(value) else None

    return value


def _save_report(report_path: str, payload: dict):
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(_sanitize_for_json(payload), f, indent=2, sort_keys=True, allow_nan=False)


def _print_top_ray_deltas(rows: list, n: int = 5):
    finite_rows = [row for row in rows if np.isfinite(row.get('delta_abs_deflection', np.nan))]
    ranked = sorted(finite_rows, key=lambda row: abs(float(row['delta_abs_deflection'])), reverse=True)
    if not ranked:
        print("Top Δ|Δφ| rays: unavailable (no finite matched comparisons)")
        return

    print(f"Top {min(n, len(ranked))} rays by |Δ|Δφ||:")
    for row in ranked[:n]:
        print(
            f"  ray={row['ray_index']:2d} y0={row['initial_y']:+7.3f} "
            f"Δ|Δφ|={row['delta_abs_deflection']:+8.4f} "
            f"{row['baseline_status']}→{row['perturbed_status']}"
        )


def main():
    cfg = CosmicRunConfig()

    print("=" * 60)
    print("COSMIC COMM: Black Hole Geodesic Tracer")
    print("=" * 60)
    
    # 1. Initialize Universe
    print(f"Initializing Universe (Kerr Black Hole M={cfg.M}, a={cfg.a})...")
    universe = CosmicUniverse(
        M=cfg.M,
        a=cfg.a,
        step_size=cfg.step_size,
        max_steps=cfg.max_steps,
        null_tolerance=cfg.null_tolerance,
        perturb_force_scale=cfg.perturb_force_scale,
        perturb_softening=cfg.perturb_softening,
    )
    
    # 2. Setup Visualization
    plotter = CosmicPlotter()
    plotter.plot_black_hole(
        universe.tracer.r_horizon,
        ergosphere_radius=universe.black_hole.ergosphere_radius(theta=np.pi / 2.0)
    )
    
    # 3. Run Baseline Simulation (No Perturbations)
    print("Running Baseline Simulation (Cyan)...")
    trajectories_base = universe.run_beam_simulation(
        start_x=cfg.start_x,
        width=cfg.beam_width,
        rays=cfg.rays,
        max_steps=cfg.max_steps,
        theta=cfg.beam_theta,
        energy=cfg.beam_energy,
    )
    
    for traj in trajectories_base:
        plotter.plot_trajectory(traj, color='cyan', alpha=0.3)

    baseline_summary = universe.summarize_trajectories(trajectories_base)
    _print_summary("Baseline", baseline_summary)
        
    # 4. Add Perturbation (Observer A places a star)
    # Place it at r=8, phi=pi/4 (45 degrees), mass=0.5
    print("Adding Perturbation (Observer A places a star)...")
    universe.add_perturbation(
        r=cfg.perturb_r,
        theta=cfg.perturb_theta,
        phi=cfg.perturb_phi,
        mass=cfg.perturb_mass,
    )
    
    # Draw the perturbation on the plot
    # Convert to Cartesian for plotting
    p_x = cfg.perturb_r * np.cos(cfg.perturb_phi)
    p_y = cfg.perturb_r * np.sin(cfg.perturb_phi)
    plotter.plot_observer(p_x, p_y, label='Observer A', color='yellow')
    
    # 5. Run Perturbed Simulation
    print("Running Perturbed Simulation (Orange)...")
    trajectories_pert = universe.run_beam_simulation(
        start_x=cfg.start_x,
        width=cfg.beam_width,
        rays=cfg.rays,
        max_steps=cfg.max_steps,
        theta=cfg.beam_theta,
        energy=cfg.beam_energy,
    )
    
    for traj in trajectories_pert:
        plotter.plot_trajectory(traj, color='orange', alpha=0.5)

    pert_summary = universe.summarize_trajectories(trajectories_pert)
    comparison = universe.compare_trajectory_sets(trajectories_base, trajectories_pert)
    ray_y, ray_delta, per_ray = _compute_per_ray_delta_data(trajectories_base, trajectories_pert)

    _print_summary("Perturbed", pert_summary)
    _print_comparison(comparison)
    _print_top_ray_deltas(per_ray, n=5)

    plotter.add_summary_text(_format_summary_block("Baseline", baseline_summary), color='cyan')
    plotter.add_summary_text(_format_summary_block("Perturbed", pert_summary), color='orange')
    plotter.add_summary_text(
        [
            "Comparison",
            f"common={int(comparison['common_rays'])}",
            f"Δ|Δφ|mean={comparison['mean_delta_abs_deflection']:.3f}",
            f"Δcap={comparison['captured_delta']:+.2f} Δesc={comparison['escaped_delta']:+.2f}",
        ],
        color='white'
    )

    plotter.plot_status_fractions(baseline_summary, pert_summary)
    plotter.plot_deflection_deltas(ray_y, ray_delta, x_label='initial y')
    plotter.auto_scale_main_axis(radial_percentile=97.5, margin=0.12)

    subtitle = (
        f"M={cfg.M:.2f}, a={cfg.a:.2f}, rays={cfg.rays}, "
        f"perturb: r={cfg.perturb_r:.1f}, φ={cfg.perturb_phi:.2f}, mass={cfg.perturb_mass:.2f}"
    )
    plotter.finalize("Photon Geodesics in Kerr Spacetime", subtitle=subtitle)

    report_payload = {
        'config': {
            'M': cfg.M,
            'a': cfg.a,
            'step_size': cfg.step_size,
            'max_steps': cfg.max_steps,
            'null_tolerance': cfg.null_tolerance,
            'start_x': cfg.start_x,
            'beam_width': cfg.beam_width,
            'rays': cfg.rays,
            'beam_theta': cfg.beam_theta,
            'beam_energy': cfg.beam_energy,
            'perturb_r': cfg.perturb_r,
            'perturb_theta': cfg.perturb_theta,
            'perturb_phi': cfg.perturb_phi,
            'perturb_mass': cfg.perturb_mass,
            'perturb_force_scale': cfg.perturb_force_scale,
            'perturb_softening': cfg.perturb_softening,
        },
        'observer': {
            'name': 'Observer A',
            'cartesian_position': {'x': p_x, 'y': p_y},
        },
        'summary': {
            'baseline': baseline_summary,
            'perturbed': pert_summary,
            'comparison': comparison,
        },
        'per_ray_delta': per_ray,
    }
    _save_report(cfg.report_path, report_payload)
        
    print(f"Simulation complete. Saving plot to '{cfg.output_path}'...")
    plotter.save(cfg.output_path, dpi=cfg.output_dpi)
    print("Plot saved.")
    print(f"Report saved to '{cfg.report_path}'.")

if __name__ == "__main__":
    main()
