"""
Visualization Module
====================
Visualizes black hole shadows and photon trajectories.
"""

import matplotlib.pyplot as plt
import numpy as np

class CosmicPlotter:
    def __init__(self):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2)
        
    def plot_black_hole(self, r_horizon):
        """Draw the event horizon."""
        circle = plt.Circle((0, 0), r_horizon, color='black', zorder=10)
        self.ax.add_artist(circle)
        # Draw ergosphere approximation (for a=0.9)
        ergo = plt.Circle((0, 0), 2.0, color='purple', alpha=0.3, zorder=5, label='Ergosphere')
        self.ax.add_artist(ergo)
        
    def plot_trajectory(self, traj, color='cyan', alpha=0.6):
        """
        Plot a single photon trajectory.
        Converts (r, phi) to Cartesian (x, y).
        """
        r = traj['r']
        phi = traj['phi']
        
        # Convert to Cartesian for plotting
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        
        self.ax.plot(x, y, color=color, alpha=alpha, linewidth=1)
        
        # Mark start and end
        self.ax.scatter(x[0], y[0], color='green', s=10, alpha=0.8) # Start
        
        if traj['status'] == 'captured':
            self.ax.scatter(x[-1], y[-1], color='red', s=10, marker='x') # Captured
            
    def show(self):
        plt.xlabel("x (M)")
        plt.ylabel("y (M)")
        plt.title("Photon Geodesics in Kerr Spacetime")
        plt.legend()
        plt.show()
