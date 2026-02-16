"""
Cosmic Communication Simulation
===============================
Simulates light bending and communication around a Kerr Black Hole.
Demonstrates how placing a perturbation (mass) alters the light paths.
"""

import numpy as np
import matplotlib.pyplot as plt
from cosmic_comm.simulation.universe import CosmicUniverse
from cosmic_comm.visualization.plotter import CosmicPlotter

def main():
    print("=" * 60)
    print("COSMIC COMM: Black Hole Geodesic Tracer")
    print("=" * 60)
    
    # 1. Initialize Universe
    print("Initializing Universe (Kerr Black Hole M=1.0, a=0.9)...")
    universe = CosmicUniverse(M=1.0, a=0.9)
    
    # 2. Setup Visualization
    plotter = CosmicPlotter()
    plotter.plot_black_hole(universe.tracer.r_horizon)
    
    # 3. Run Baseline Simulation (No Perturbations)
    print("Running Baseline Simulation (Cyan)...")
    trajectories_base = universe.run_beam_simulation(start_x=20.0, width=15.0, rays=30)
    
    for traj in trajectories_base:
        plotter.plot_trajectory(traj, color='cyan', alpha=0.3)
        
    # 4. Add Perturbation (Observer A places a star)
    # Place it at r=10, phi=pi/4 (45 degrees), mass=0.5
    print("Adding Perturbation (Observer A places a star)...")
    universe.add_perturbation(r=8.0, theta=np.pi/2, phi=np.pi/4, mass=0.5)
    
    # Draw the perturbation on the plot
    # Convert to Cartesian for plotting
    p_x = 8.0 * np.cos(np.pi/4)
    p_y = 8.0 * np.sin(np.pi/4)
    plotter.ax.scatter(p_x, p_y, color='yellow', s=100, label='Perturbation', zorder=20)
    plotter.ax.text(p_x+1, p_y, "Observer A", color='yellow')
    
    # 5. Run Perturbed Simulation
    print("Running Perturbed Simulation (Orange)...")
    trajectories_pert = universe.run_beam_simulation(start_x=20.0, width=15.0, rays=30)
    
    for traj in trajectories_pert:
        plotter.plot_trajectory(traj, color='orange', alpha=0.5)
        
    print("Simulation complete. Saving plot to 'cosmic_comm_demo.png'...")
    plt.savefig('cosmic_comm_demo.png')
    print("Plot saved.")

if __name__ == "__main__":
    main()
