"""
Temporal Plot Visualization
============================
Visualizes emergent time τ versus simulation time t, and temporal loops ΔT.

Shows:
1. Real and imaginary components of emergent time
2. Phase evolution over time
3. Winding number progression
4. Temporal displacement ΔT from detected loops
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional


class TemporalPlotVisualizer:
    """
    Visualizes temporal phenomena: τ vs t, winding, ΔT loops.
    """
    
    def __init__(self, ax: Optional[plt.Axes] = None):
        """
        Initialize the temporal plot visualizer.
        
        Args:
            ax: Matplotlib axes to draw on (creates new if None)
        """
        if ax is None:
            self.fig, self.ax = plt.subplots(figsize=(10, 6))
        else:
            self.ax = ax
            self.fig = None
    
    def plot_emergent_time(self, history: Dict[str, np.ndarray]):
        """
        Plot emergent time evolution τ(t).
        
        Args:
            history: Dictionary with 'time', 'emergent_time_real', 'emergent_time_imag'
        """
        self.ax.clear()
        
        time = history.get('time', np.array([]))
        tau_real = history.get('emergent_time_real', np.array([]))
        tau_imag = history.get('emergent_time_imag', np.array([]))
        
        if len(time) == 0 or len(tau_real) == 0:
            self.ax.set_title("Emergent Time τ vs Simulation Time t")
            self.ax.set_xlabel("Simulation Time t")
            self.ax.set_ylabel("Emergent Time τ")
            self.ax.grid(True, alpha=0.3)
            return
        
        # Ensure arrays match in length (take minimum)
        min_len = min(len(time), len(tau_real), len(tau_imag))
        time = time[-min_len:]
        tau_real = tau_real[-min_len:]
        tau_imag = tau_imag[-min_len:]
        
        # Plot real and imaginary components
        self.ax.plot(time, tau_real, 'b-', label='τ (real)', lw=2, alpha=0.8)
        self.ax.plot(time, tau_imag, 'r-', label='τ (imag)', lw=2, alpha=0.8)
        
        # Plot magnitude
        tau_mag = np.sqrt(tau_real**2 + tau_imag**2)
        self.ax.plot(time, tau_mag, 'g--', label='|τ|', lw=1.5, alpha=0.6)
        
        # Formatting
        self.ax.set_xlabel("Simulation Time t (s)", fontsize=10)
        self.ax.set_ylabel("Emergent Time τ", fontsize=10)
        self.ax.set_title("Emergent Time Evolution", fontsize=12)
        self.ax.legend(loc='best', fontsize=9)
        self.ax.grid(True, alpha=0.3)
    
    def plot_phase_evolution(self, history: Dict[str, np.ndarray]):
        """
        Plot phase angle evolution over time.
        
        Args:
            history: Dictionary with 'time', 'phase'
        """
        self.ax.clear()
        
        time = history.get('time', np.array([]))
        phase = history.get('phase', np.array([]))
        
        if len(time) == 0:
            self.ax.set_title("Phase Evolution φ(t)")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Phase (radians)")
            return
        
        # Unwrap phase for continuous plotting
        phase_unwrapped = np.unwrap(phase)
        
        self.ax.plot(time, phase, 'b-', alpha=0.3, label='Phase (wrapped)')
        self.ax.plot(time, phase_unwrapped, 'r-', lw=2, label='Phase (unwrapped)')
        
        # Mark 2π intervals
        if len(phase_unwrapped) > 0:
            y_min, y_max = phase_unwrapped.min(), phase_unwrapped.max()
            for n in range(int(y_min / (2*np.pi)) - 1, int(y_max / (2*np.pi)) + 2):
                self.ax.axhline(n * 2 * np.pi, color='gray', linestyle=':', alpha=0.5)
        
        self.ax.set_xlabel("Simulation Time t (s)", fontsize=10)
        self.ax.set_ylabel("Phase φ (radians)", fontsize=10)
        self.ax.set_title("Phase Evolution", fontsize=12)
        self.ax.legend(loc='best', fontsize=9)
        self.ax.grid(True, alpha=0.3)
    
    def plot_winding_history(self, history: Dict[str, np.ndarray]):
        """
        Plot winding number evolution over time.
        
        Args:
            history: Dictionary with 'time', 'winding'
        """
        self.ax.clear()
        
        time = history.get('time', np.array([]))
        winding = history.get('winding', np.array([]))
        
        if len(time) == 0 or len(winding) == 0:
            self.ax.set_title("Winding Number n(t)")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Winding Number")
            return
        
        # Trim time to match winding length
        time_trimmed = time[-len(winding):]
        
        self.ax.plot(time_trimmed, winding, 'purple', lw=2, marker='o', markersize=3)
        self.ax.axhline(0, color='k', linestyle='-', lw=0.5, alpha=0.3)
        
        # Mark integer winding numbers
        if len(winding) > 0:
            for n in range(int(np.floor(winding.min())), int(np.ceil(winding.max())) + 1):
                self.ax.axhline(n, color='gray', linestyle=':', alpha=0.5)
        
        self.ax.set_xlabel("Simulation Time t (s)", fontsize=10)
        self.ax.set_ylabel("Winding Number n", fontsize=10)
        self.ax.set_title("Winding Number Evolution", fontsize=12)
        self.ax.grid(True, alpha=0.3)
    
    def plot_order_disorder_balance(self, history: Dict[str, np.ndarray]):
        """
        Plot order and disorder parameters over time.
        
        Args:
            history: Dictionary with 'time', 'order', 'disorder'
        """
        self.ax.clear()
        
        time = history.get('time', np.array([]))
        order = history.get('order', np.array([]))
        disorder = history.get('disorder', np.array([]))
        
        if len(time) == 0 or len(order) == 0:
            self.ax.set_title("Order-Disorder Balance")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Parameter Value")
            return
        
        # Ensure arrays match in length
        min_len = min(len(time), len(order), len(disorder))
        time = time[-min_len:]
        order = order[-min_len:]
        disorder = disorder[-min_len:]
        
        self.ax.plot(time, order, 'b-', label='Order (Ω)', lw=2)
        self.ax.plot(time, disorder, 'r-', label='Disorder (Ω̄)', lw=2)
        
        # Fill area between them
        self.ax.fill_between(time, order, disorder, alpha=0.2, color='purple')
        
        self.ax.set_xlabel("Simulation Time t (s)", fontsize=10)
        self.ax.set_ylabel("Parameter Value", fontsize=10)
        self.ax.set_title("Order-Disorder Balance Over Time", fontsize=12)
        self.ax.legend(loc='best', fontsize=9)
        self.ax.set_ylim(0, 1)
        self.ax.grid(True, alpha=0.3)
