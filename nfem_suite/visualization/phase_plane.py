"""
Phase Plane Visualization
==========================
Argand diagram (complex plane) visualization of entropy states.

Plots the complex entropy states Z = |S| · e^(iφ) on the complex plane:
- Real axis = Order
- Imaginary axis = Disorder
- Each point represents a system state
- Trajectory shows evolution through order-disorder space
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional


class PhasePlaneVisualizer:
    """
    Visualizes complex entropy states on the Argand diagram.
    """
    
    def __init__(self, ax: Optional[plt.Axes] = None):
        """
        Initialize the phase plane visualizer.
        
        Args:
            ax: Matplotlib axes to draw on (creates new if None)
        """
        if ax is None:
            self.fig, self.ax = plt.subplots(figsize=(6, 6))
        else:
            self.ax = ax
            self.fig = None
    
    def plot(self, complex_states: List[complex], title: str = "Complex Entropy Phase Plane"):
        """
        Plot complex entropy states on the Argand diagram.
        
        Args:
            complex_states: List of complex entropy states
            title: Plot title
        """
        self.ax.clear()
        
        if len(complex_states) == 0:
            self.ax.set_title(title)
            self.ax.set_xlabel("Order (Real)")
            self.ax.set_ylabel("Disorder (Imaginary)")
            self.ax.grid(True, alpha=0.3)
            return
        
        # Extract real and imaginary parts
        real_parts = [z.real for z in complex_states]
        imag_parts = [z.imag for z in complex_states]
        
        # Plot trajectory (older points faded)
        if len(complex_states) > 1:
            # Color by time (older = blue, newer = red)
            colors = plt.cm.viridis(np.linspace(0, 1, len(complex_states)))
            
            for i in range(len(complex_states) - 1):
                self.ax.plot(
                    [real_parts[i], real_parts[i+1]],
                    [imag_parts[i], imag_parts[i+1]],
                    c=colors[i], alpha=0.5, lw=1
                )
        
        # Plot current state (large marker)
        self.ax.scatter(
            real_parts[-1], imag_parts[-1],
            c='red', s=100, marker='o', edgecolors='black', zorder=10,
            label='Current State'
        )
        
        # Plot origin
        self.ax.scatter(0, 0, c='gray', s=50, marker='x', zorder=5, label='Origin')
        
        # Draw unit circle for reference
        theta = np.linspace(0, 2*np.pi, 100)
        self.ax.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.2, lw=1, label='Unit Circle')
        
        # Draw axes
        max_val = max(max(abs(z.real) for z in complex_states), 
                     max(abs(z.imag) for z in complex_states), 1.0) * 1.2
        self.ax.axhline(0, color='k', lw=0.5, alpha=0.3)
        self.ax.axvline(0, color='k', lw=0.5, alpha=0.3)
        
        # Labels and formatting
        self.ax.set_xlabel("Order (Real Axis)", fontsize=10)
        self.ax.set_ylabel("Disorder (Imaginary Axis)", fontsize=10)
        self.ax.set_title(title, fontsize=12)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right', fontsize=8)
        
        # Set limits
        self.ax.set_xlim(-max_val, max_val)
        self.ax.set_ylim(-max_val, max_val)
    
    def plot_with_statistics(self, complex_states: List[complex], 
                            winding_number: float,
                            emergent_time: complex):
        """
        Plot phase plane with additional statistics overlay.
        
        Args:
            complex_states: List of complex entropy states
            winding_number: Winding number around origin
            emergent_time: Current emergent time τ
        """
        self.plot(complex_states, title="Complex Entropy Phase Plane")
        
        # Add text box with statistics
        stats_text = f"Winding #: {winding_number:.2f}\n"
        stats_text += f"τ (real): {emergent_time.real:.2f}\n"
        stats_text += f"τ (imag): {emergent_time.imag:.2f}\n"
        stats_text += f"|τ|: {abs(emergent_time):.2f}"
        
        self.ax.text(
            0.02, 0.98, stats_text,
            transform=self.ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7)
        )
