"""
Enhanced Dashboard
==================
Comprehensive visualization of the Enthalpy Map system with:
- Physical map with enthalpy field overlay
- Complex entropy phase plane
- Temporal evolution plots
- Vortex channel visualization
- Order-disorder dynamics
"""

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT
from nfem_suite.visualization.phase_plane import PhasePlaneVisualizer
from nfem_suite.visualization.temporal_plot import TemporalPlotVisualizer


class Dashboard:
    """
    Enhanced multi-panel dashboard for the NFEM/Enthalpy Map system.
    """
    
    def __init__(self, mode='full'):
        """
        Initialize the dashboard.
        
        Args:
            mode: 'full' for 6-panel view, 'simple' for 2-panel (backward compatible)
        """
        plt.ion()
        self.mode = mode
        
        if mode == 'full':
            # 2x3 grid layout
            self.fig = plt.figure(figsize=(20, 12))
            gs = self.fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
            
            # Top row
            self.ax_map = self.fig.add_subplot(gs[0, 0])           # Physical map
            self.ax_enthalpy = self.fig.add_subplot(gs[0, 1])      # Enthalpy field
            self.ax_phase = self.fig.add_subplot(gs[0, 2])         # Phase plane
            
            # Bottom row
            self.ax_stats = self.fig.add_subplot(gs[1, 0])         # Traditional entropy stats
            self.ax_temporal = self.fig.add_subplot(gs[1, 1])      # Temporal evolution
            self.ax_duality = self.fig.add_subplot(gs[1, 2])       # Order-disorder
            
            # Visualizer helpers
            self.phase_viz = PhasePlaneVisualizer(ax=self.ax_phase)
            self.temporal_viz = TemporalPlotVisualizer(ax=self.ax_temporal)
            
        else:  # simple mode (backward compatible)
            self.fig, (self.ax_map, self.ax_stats) = plt.subplots(1, 2, figsize=(15, 7))
        
        # History tracking
        self.entropy_history = []
        self.energy_entropy_history = []
        self.struct_entropy_history = []
        
        # Colorbar reference
        self.cbar_enthalpy = None
    
    def update(self, network, gradients, k_entropy, e_entropy, s_entropy, triangulation, time, control=None,
               enthalpy_field=None, duality_space=None, vortex_channel=None):
        """
        Update all dashboard panels.
        
        Args:
            network: Network object
            gradients: Velocity gradients
            k_entropy: Kinetic entropy
            e_entropy: Energetic entropy
            s_entropy: Structural entropy
            triangulation: Delaunay triangulation
            time: Simulation time
            control: Control system (optional)
            enthalpy_field: EnthalpyField object (optional)
            duality_space: DualitySpace object (optional)
            vortex_channel: VortexChannel object (optional)
        """
        if self.mode == 'simple':
            self._update_simple(network, gradients, k_entropy, e_entropy, s_entropy, 
                              triangulation, time, control)
        else:
            self._update_full(network, gradients, k_entropy, e_entropy, s_entropy,
                            triangulation, time, control, enthalpy_field, 
                            duality_space, vortex_channel)
        
        plt.draw()
        plt.pause(0.001)
    
    def _update_simple(self, network, gradients, k_entropy, e_entropy, s_entropy, 
                      triangulation, time, control):
        """Update simple 2-panel dashboard (backward compatible)."""
        self.ax_map.clear()
        self.ax_stats.clear()
        
        # Panel 1: Map View
        self._draw_map_panel(self.ax_map, network, gradients, triangulation, time, control)
        
        # Panel 2: Stats
        self._draw_stats_panel(self.ax_stats, k_entropy, e_entropy, s_entropy)
    
    def _update_full(self, network, gradients, k_entropy, e_entropy, s_entropy,
                    triangulation, time, control, enthalpy_field, duality_space, vortex_channel):
        """Update full 6-panel dashboard."""
        # Clear all axes
        for ax in [self.ax_map, self.ax_enthalpy, self.ax_stats, self.ax_duality]:
            ax.clear()
        
        # Panel 1: Physical Map
        self._draw_map_panel(self.ax_map, network, gradients, triangulation, time, control)
        
        # Panel 2: Enthalpy Field
        self._draw_enthalpy_panel(self.ax_enthalpy, enthalpy_field, network, vortex_channel)
        
        # Panel 3: Phase Plane (handled by visualizer)
        if duality_space:
            states = list(duality_space.complex_state_history)
            self.phase_viz.plot_with_statistics(
                states,
                duality_space.winding_number,
                duality_space.emergent_time
            )
        
        # Panel 4: Traditional Entropy Stats
        self._draw_stats_panel(self.ax_stats, k_entropy, e_entropy, s_entropy)
        
        # Panel 5: Temporal Evolution (handled by visualizer)
        if duality_space and len(duality_space.time_history) > 0:
            history = duality_space.get_history_arrays()
            self.temporal_viz.plot_emergent_time(history)
        
        # Panel 6: Order-Disorder Balance
        if duality_space and len(duality_space.time_history) > 0:
            history = duality_space.get_history_arrays()
            self._draw_duality_panel(self.ax_duality, history)
    
    def _draw_map_panel(self, ax, network, gradients, triangulation, time, control):
        """Draw the physical map panel."""
        ax.set_title(f"Physical System Map (t={time:.1f}s)", fontsize=11, fontweight='bold')
        ax.set_xlim(0, GRID_WIDTH)
        ax.set_ylim(0, GRID_HEIGHT)
        ax.set_aspect('equal')
        ax.set_xlabel("X Position", fontsize=9)
        ax.set_ylabel("Y Position", fontsize=9)
        
        # Draw Control Target
        if control:
            circle = plt.Circle(control.target_pos, control.target_radius, 
                              color='cyan', fill=False, lw=2, linestyle='--', label='Control Zone')
            ax.add_artist(circle)
            ax.plot(control.target_pos[0], control.target_pos[1], 'cX', markersize=10)

        positions = network.get_positions()
        if len(positions) > 0:
            # Draw Mesh
            if triangulation:
                verts = positions[triangulation.simplices]
                pc = PolyCollection(verts, facecolors='cyan', edgecolors='none', alpha=0.1)
                ax.add_collection(pc)

            # Draw Gradient Lines
            for g in gradients:
                shear = g['gradient']
                color = plt.cm.inferno(min(shear / 3.0, 1.0)) 
                ax.plot(
                    [g['pos_u'][0], g['pos_v'][0]], 
                    [g['pos_u'][1], g['pos_v'][1]], 
                    c=color, alpha=0.4, lw=1
                )
            
            # Draw Nodes
            active_nodes = network.get_active_nodes()
            if active_nodes:
                pos = np.array([n.position for n in active_nodes])
                batt = np.array([n.battery_level for n in active_nodes])
                
                sc = ax.scatter(pos[:,0], pos[:,1], c=batt, cmap='viridis', s=40, 
                              edgecolors='k', zorder=3, label='Nodes')

                # Velocity Vectors
                vel = np.array([n.velocity for n in active_nodes])
                ax.quiver(pos[:,0], pos[:,1], vel[:,0], vel[:,1], 
                         color='white', alpha=0.6, width=0.003)

        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.2)
    
    def _draw_enthalpy_panel(self, ax, enthalpy_field, network, vortex_channel):
        """Draw the enthalpy field panel."""
        ax.set_title("Enthalpy Field H(x,t) & Vortex Channel", fontsize=11, fontweight='bold')
        ax.set_xlabel("X Position", fontsize=9)
        ax.set_ylabel("Y Position", fontsize=9)
        ax.set_aspect('equal')
        
        if enthalpy_field:
            # Draw enthalpy field as heatmap
            im = ax.imshow(enthalpy_field.enthalpy_field.T, 
                          origin='lower',
                          extent=[0, GRID_WIDTH, 0, GRID_HEIGHT],
                          cmap='hot', alpha=0.7, aspect='auto')
            
            # Add colorbar only once
            if self.cbar_enthalpy is None:
                self.cbar_enthalpy = self.fig.colorbar(im, ax=ax, label='Enthalpy', fraction=0.046, pad=0.04)
            else:
                # Update the colorbar with the new image mappable
                self.cbar_enthalpy.update_normal(im)
            
            # Draw gradient field as quiver
            skip = 3  # Subsample for clarity
            X, Y = enthalpy_field.grid_x[::skip, ::skip], enthalpy_field.grid_y[::skip, ::skip]
            U = enthalpy_field.gradient_field[::skip, ::skip, 0]
            V = enthalpy_field.gradient_field[::skip, ::skip, 1]
            ax.quiver(X, Y, U, V, alpha=0.4, color='cyan', scale=1000)
        
        # Draw vortex channel if available
        if vortex_channel:
            # Draw vortex center
            ax.scatter(vortex_channel.vortex_center[0], vortex_channel.vortex_center[1],
                      c='purple', s=200, marker='*', edgecolors='white', linewidths=2,
                      label='Vortex', zorder=10)
            
            # Draw vortex radius
            circle = plt.Circle(vortex_channel.vortex_center, vortex_channel.vortex_radius,
                              color='purple', fill=False, lw=2, linestyle=':')
            ax.add_artist(circle)
            
            # Draw signal paths if positions are set
            if vortex_channel.source_a_position is not None:
                ax.scatter(vortex_channel.source_a_position[0], 
                          vortex_channel.source_a_position[1],
                          c='green', s=100, marker='s', label='Source A', zorder=5)
            
            if vortex_channel.receiver_b_position is not None:
                ax.scatter(vortex_channel.receiver_b_position[0],
                          vortex_channel.receiver_b_position[1],
                          c='red', s=100, marker='o', label='Receiver B', zorder=5)
            
            # Draw communication paths
            forward_path, backward_path = vortex_channel.visualize_signal_paths()
            if len(forward_path) > 0:
                ax.plot(forward_path[:, 0], forward_path[:, 1], 
                       'g--', lw=2, alpha=0.6, label='A→V→B')
                ax.plot(backward_path[:, 0], backward_path[:, 1],
                       'r--', lw=2, alpha=0.6, label='B→V→A')
        
        # Draw nodes
        positions = network.get_positions()
        if len(positions) > 0:
            ax.scatter(positions[:, 0], positions[:, 1], c='white', s=10, 
                      alpha=0.5, edgecolors='none')
        
        ax.legend(loc='upper right', fontsize=8)
        ax.set_xlim(0, GRID_WIDTH)
        ax.set_ylim(0, GRID_HEIGHT)
        ax.grid(True, alpha=0.2)
    
    def _draw_stats_panel(self, ax, k_entropy, e_entropy, s_entropy):
        """Draw traditional entropy statistics panel."""
        self.entropy_history.append(k_entropy)
        self.energy_entropy_history.append(e_entropy)
        self.struct_entropy_history.append(s_entropy)
        
        if len(self.entropy_history) > 100:
            self.entropy_history.pop(0)
            self.energy_entropy_history.pop(0)
            self.struct_entropy_history.pop(0)
        
        ax.plot(self.entropy_history, label="Kinetic (Turbulence)", c='red', lw=2)
        ax.plot(self.energy_entropy_history, label="Energetic (Inequality)", c='green', lw=2)
        ax.plot(self.struct_entropy_history, label="Structural (Mesh)", c='blue', lw=2)
        ax.set_title("Traditional Entropy Metrics", fontsize=11, fontweight='bold')
        ax.set_xlabel("Time Step", fontsize=9)
        ax.set_ylabel("Entropy (Shannon Bits)", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _draw_duality_panel(self, ax, history):
        """Draw order-disorder balance panel."""
        time = history.get('time', np.array([]))
        order = history.get('order', np.array([]))
        disorder = history.get('disorder', np.array([]))
        
        if len(time) == 0:
            ax.set_title("Order-Disorder Duality")
            return
        
        ax.plot(time, order, 'b-', label='Order (Ω)', lw=2)
        ax.plot(time, disorder, 'r-', label='Disorder (Ω̄)', lw=2)
        ax.fill_between(time, order, disorder, alpha=0.2, color='purple')
        
        ax.set_title("Order-Disorder Balance", fontsize=11, fontweight='bold')
        ax.set_xlabel("Simulation Time t (s)", fontsize=9)
        ax.set_ylabel("Parameter Value", fontsize=9)
        ax.legend(fontsize=8)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)
    
    def show(self):
        """Display the dashboard."""
        plt.show()
