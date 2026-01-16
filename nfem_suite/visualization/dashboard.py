import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT

class Dashboard:
    def __init__(self):
        plt.ion()
        self.fig, (self.ax_map, self.ax_stats) = plt.subplots(1, 2, figsize=(15, 7))
        self.entropy_history = []
        self.energy_entropy_history = []
        self.struct_entropy_history = []
        
    def update(self, network, gradients, k_entropy, e_entropy, s_entropy, triangulation, time, control=None):
        self.ax_map.clear()
        self.ax_stats.clear()
        
        # 1. Map View
        self.ax_map.set_title(f"NFEM: Entropic Collapse & Macro-Fibre (t={time:.1f}s)")
        self.ax_map.set_xlim(0, GRID_WIDTH)
        self.ax_map.set_ylim(0, GRID_HEIGHT)
        self.ax_map.set_aspect('equal')
        
        # Draw Control Target (The "Hot Potato")
        if control:
            circle = plt.Circle(control.target_pos, control.target_radius, 
                              color='cyan', fill=False, lw=2, linestyle='--', label='Control Zone')
            self.ax_map.add_artist(circle)
            # Plot center point of control
            self.ax_map.plot(control.target_pos[0], control.target_pos[1], 'cX', markersize=10)

        positions = network.get_positions()
        if len(positions) > 0:
            # Draw Filled Planes (The Mesh)
            if triangulation:
                verts = positions[triangulation.simplices]
                # Draw semi-transparent planes to visualize density/overlap
                pc = PolyCollection(verts, facecolors='cyan', edgecolors='none', alpha=0.1)
                self.ax_map.add_collection(pc)

            # Draw Connections (Mesh)
            for g in gradients:
                # Color line by shear intensity (gradient) - This represents Folding/Stretching
                shear = g['gradient']
                # Use a colormap that highlights high shear (Folding)
                color = plt.cm.inferno(min(shear / 3.0, 1.0)) 
                self.ax_map.plot(
                    [g['pos_u'][0], g['pos_v'][0]], 
                    [g['pos_u'][1], g['pos_v'][1]], 
                    c=color, alpha=0.4, lw=1
                )
            
            # Draw Nodes
            active_nodes = network.get_active_nodes()
            if active_nodes:
                pos = np.array([n.position for n in active_nodes])
                batt = np.array([n.battery_level for n in active_nodes])
                
                # Draw nodes
                sc = self.ax_map.scatter(pos[:,0], pos[:,1], c=batt, cmap='viridis', s=40, edgecolors='k', zorder=3)

                # Draw Velocity Vectors (The Flow)
                vel = np.array([n.velocity for n in active_nodes])
                self.ax_map.quiver(pos[:,0], pos[:,1], vel[:,0], vel[:,1], color='white', alpha=0.6, width=0.003)

        self.ax_map.legend(loc='upper right')

        # 2. Stats View
        self.entropy_history.append(k_entropy)
        self.energy_entropy_history.append(e_entropy)
        self.struct_entropy_history.append(s_entropy)
        
        if len(self.entropy_history) > 100:
            self.entropy_history.pop(0)
            self.energy_entropy_history.pop(0)
            self.struct_entropy_history.pop(0)
            
        self.ax_stats.plot(self.entropy_history, label="Kinetic (Turbulence)", c='red')
        self.ax_stats.plot(self.energy_entropy_history, label="Energetic (Inequality)", c='green')
        self.ax_stats.plot(self.struct_entropy_history, label="Structural (Mesh Disorder)", c='blue')
        self.ax_stats.set_title("Entropic Structure Metrics")
        self.ax_stats.set_xlabel("Time Step")
        self.ax_stats.set_ylabel("Entropy (Bits)")
        self.ax_stats.legend()
        self.ax_stats.grid(True, alpha=0.3)
        
        plt.draw()
        plt.pause(0.001)

    def show(self):
        plt.show()
