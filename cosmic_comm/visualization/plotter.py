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
        self._start_marker_plotted = False
        self._captured_marker_plotted = False
        self._summary_anchor_y = 0.98
        self.ax.grid(True, alpha=0.2)
        
    def plot_black_hole(self, r_horizon, ergosphere_radius=None):
        """Draw the event horizon."""
        circle = plt.Circle((0, 0), r_horizon, color='black', zorder=10, label='Event Horizon')
        self.ax.add_artist(circle)

        if ergosphere_radius is None:
            ergosphere_radius = 2.0

        ergo = plt.Circle((0, 0), ergosphere_radius, color='purple', alpha=0.3, zorder=5, label='Ergosphere')
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
        start_label = 'Start' if not self._start_marker_plotted else None
        self.ax.scatter(x[0], y[0], color='green', s=10, alpha=0.8, label=start_label) # Start
        self._start_marker_plotted = True
        
        if traj['status'] == 'captured':
            cap_label = 'Captured' if not self._captured_marker_plotted else None
            self.ax.scatter(x[-1], y[-1], color='red', s=10, marker='x', label=cap_label) # Captured
            self._captured_marker_plotted = True

    def add_summary_text(self, lines, color='white'):
        """Render one summary text block in the top-left of the axes."""
        if not lines:
            return

        text = "\n".join(str(line) for line in lines)
        self.ax.text(
            0.02,
            self._summary_anchor_y,
            text,
            transform=self.ax.transAxes,
            va='top',
            ha='left',
            fontsize=9,
            color=color,
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.45, edgecolor='white')
        )
        line_height = 0.045
        block_margin = 0.03
        self._summary_anchor_y -= (line_height * len(lines) + block_margin)
            
    def show(self):
        plt.xlabel("x (M)")
        plt.ylabel("y (M)")
        plt.title("Photon Geodesics in Kerr Spacetime")
        plt.legend()
        plt.show()
