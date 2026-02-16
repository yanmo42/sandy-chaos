"""
Cosmic Communication Simulation
===============================
Simulates light bending and communication around a Kerr Black Hole.
Demonstrates how placing a perturbation (mass) alters the light paths.
"""

import numpy as np
import matplotlib.pyplot as plt
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
        f"Δcapt={comparison['captured_delta']:+.2f} "
        f"Δesc={comparison['escaped_delta']:+.2f}"
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
    plotter.ax.scatter(p_x, p_y, color='yellow', s=100, label='Perturbation', zorder=20)
    plotter.ax.text(p_x+1, p_y, "Observer A", color='yellow')
    
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

    _print_summary("Perturbed", pert_summary)
    _print_comparison(comparison)

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
        
    print(f"Simulation complete. Saving plot to '{cfg.output_path}'...")
    plt.savefig(cfg.output_path)
    print("Plot saved.")

if __name__ == "__main__":
    main()
