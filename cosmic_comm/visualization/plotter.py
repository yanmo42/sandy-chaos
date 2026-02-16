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

        self.fig = plt.figure(figsize=(14, 8), constrained_layout=True)
        grid = self.fig.add_gridspec(
            nrows=3,
            ncols=2,
            width_ratios=[3.8, 2.2],
            height_ratios=[1.3, 1.0, 1.0],
        )

        # Main trajectory axis (left)
        self.ax = self.fig.add_subplot(grid[:, 0])
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2)

        # Right-side descriptive panels
        self.summary_ax = self.fig.add_subplot(grid[0, 1])
        self.status_ax = self.fig.add_subplot(grid[1, 1])
        self.delta_ax = self.fig.add_subplot(grid[2, 1])

        self.summary_ax.set_title("Run Summary", fontsize=11, pad=8)
        self.summary_ax.axis('off')

        self._start_marker_plotted = False
        self._captured_marker_plotted = False
        self._summary_anchor_y = 0.98
        self._x_samples = []
        self._y_samples = []
        self._required_radius = 2.0

    def _register_points(self, x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        if np.any(mask):
            self._x_samples.append(x[mask])
            self._y_samples.append(y[mask])

    def _update_required_radius(self, x, y):
        radius = float(np.sqrt(x**2 + y**2))
        if np.isfinite(radius):
            self._required_radius = max(self._required_radius, radius)
        
    def plot_black_hole(self, r_horizon, ergosphere_radius=None):
        """Draw the event horizon."""
        circle = plt.Circle((0, 0), r_horizon, color='black', zorder=10, label='Event Horizon')
        self.ax.add_artist(circle)

        if ergosphere_radius is None:
            ergosphere_radius = 2.0

        ergo = plt.Circle((0, 0), ergosphere_radius, color='purple', alpha=0.3, zorder=5, label='Ergosphere')
        self.ax.add_artist(ergo)

        self._required_radius = max(self._required_radius, float(ergosphere_radius), float(r_horizon))

    def plot_observer(self, x, y, label='Observer A', color='yellow'):
        """Plot an observer/perturbation marker with a readable label."""
        self.ax.scatter(x, y, color=color, s=110, label='Perturbation', zorder=20)

        x_offset = 12 if x >= 0 else -12
        y_offset = 10 if y >= 0 else -10
        self.ax.annotate(
            label,
            xy=(x, y),
            xytext=(x_offset, y_offset),
            textcoords='offset points',
            color=color,
            fontsize=10,
            arrowprops=dict(arrowstyle='->', color=color, alpha=0.7, lw=1.0),
            ha='left' if x >= 0 else 'right',
            va='bottom' if y >= 0 else 'top',
            zorder=21,
        )

        self._update_required_radius(x, y)
        
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

        self._register_points(x, y)
        
        self.ax.plot(x, y, color=color, alpha=alpha, linewidth=1.1)
        
        # Mark start and end
        start_label = 'Start' if not self._start_marker_plotted else None
        self.ax.scatter(x[0], y[0], color='green', s=12, alpha=0.8, label=start_label) # Start
        self._start_marker_plotted = True
        
        if traj['status'] == 'captured':
            cap_label = 'Captured' if not self._captured_marker_plotted else None
            self.ax.scatter(x[-1], y[-1], color='red', s=14, marker='x', label=cap_label) # Captured
            self._captured_marker_plotted = True

    def auto_scale_main_axis(self, radial_percentile=97.5, margin=0.12):
        """Set readable symmetric limits while clipping extreme outliers."""
        if not self._x_samples or not self._y_samples:
            return

        x = np.concatenate(self._x_samples)
        y = np.concatenate(self._y_samples)
        r = np.sqrt(x**2 + y**2)
        r = r[np.isfinite(r)]

        if r.size == 0:
            return

        r_clip = float(np.nanpercentile(r, radial_percentile))
        if not np.isfinite(r_clip) or r_clip <= 0:
            r_clip = float(np.nanmax(r))

        max_radius = max(r_clip, self._required_radius) * (1.0 + float(margin))
        self.ax.set_xlim(-max_radius, max_radius)
        self.ax.set_ylim(-max_radius, max_radius)

    def plot_status_fractions(self, baseline_summary, pert_summary):
        """Compare baseline and perturbed run outcomes."""
        keys = [
            'captured_fraction',
            'escaped_fraction',
            'max_steps_fraction',
            'numerical_error_fraction',
            'constraint_violation_fraction',
        ]
        labels = ['capt', 'esc', 'max', 'num err', 'constraint']

        baseline_vals = np.array([baseline_summary.get(k, np.nan) for k in keys], dtype=float)
        pert_vals = np.array([pert_summary.get(k, np.nan) for k in keys], dtype=float)
        baseline_vals = np.nan_to_num(baseline_vals, nan=0.0)
        pert_vals = np.nan_to_num(pert_vals, nan=0.0)

        ax = self.status_ax
        ax.cla()
        x = np.arange(len(labels), dtype=float)
        width = 0.38

        ax.bar(x - width / 2.0, baseline_vals, width=width, color='cyan', alpha=0.75, label='baseline')
        ax.bar(x + width / 2.0, pert_vals, width=width, color='orange', alpha=0.75, label='perturbed')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha='right')
        ax.set_ylim(0.0, 1.0)
        ax.set_ylabel('fraction')
        ax.set_title('Outcome Fractions')
        ax.grid(True, axis='y', alpha=0.2)
        ax.legend(loc='upper right', fontsize=8, framealpha=0.35)

    def plot_deflection_deltas(self, x_positions, delta_values, x_label='initial y'):
        """Show how perturbation changes |Δφ| on a per-ray basis."""
        x_positions = np.asarray(x_positions, dtype=float)
        delta_values = np.asarray(delta_values, dtype=float)

        ax = self.delta_ax
        ax.cla()

        if x_positions.size == 0 or delta_values.size == 0:
            ax.text(0.5, 0.5, 'No matched rays to compare', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Deflection Delta')
            return

        order = np.argsort(x_positions)
        x_sorted = x_positions[order]
        delta_sorted = delta_values[order]
        colors = np.where(delta_sorted >= 0.0, 'orange', 'deepskyblue')

        ax.axhline(0.0, color='white', alpha=0.35, lw=1.0)
        ax.scatter(x_sorted, delta_sorted, c=colors, s=28, alpha=0.9)
        if len(x_sorted) > 1:
            ax.plot(x_sorted, delta_sorted, color='white', alpha=0.2, lw=0.9)

        max_abs = float(np.nanmax(np.abs(delta_sorted))) if np.any(np.isfinite(delta_sorted)) else 1.0
        y_lim = max(0.05, max_abs * 1.2)
        ax.set_ylim(-y_lim, y_lim)
        ax.set_xlabel(x_label)
        ax.set_ylabel('Δ|Δφ|')
        ax.set_title('Per-Ray Deflection Change')
        ax.grid(True, alpha=0.2)

    def add_summary_text(self, lines, color='white'):
        """Render one summary text block in the right-side summary panel."""
        if not lines:
            return

        text = "\n".join(str(line) for line in lines)
        self.summary_ax.text(
            0.03,
            self._summary_anchor_y,
            text,
            transform=self.summary_ax.transAxes,
            va='top',
            ha='left',
            fontsize=9,
            color=color,
            family='monospace',
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.45, edgecolor='white')
        )
        line_height = 0.055
        block_margin = 0.04
        self._summary_anchor_y -= (line_height * len(lines) + block_margin)

    def finalize(self, title, subtitle=None):
        self.ax.set_xlabel("x (M)")
        self.ax.set_ylabel("y (M)")
        self.ax.set_title(title)

        if subtitle:
            self.fig.suptitle(subtitle, fontsize=10, y=0.995, alpha=0.85)

        handles, labels = self.ax.get_legend_handles_labels()
        unique = {}
        for handle, label in zip(handles, labels):
            if label and label not in unique:
                unique[label] = handle
        if unique:
            self.ax.legend(unique.values(), unique.keys(), loc='lower right', framealpha=0.35, fontsize=8)

    def save(self, path, dpi=180):
        self.fig.savefig(path, dpi=dpi, bbox_inches='tight')
            
    def show(self):
        self.finalize("Photon Geodesics in Kerr Spacetime")
        plt.show()
