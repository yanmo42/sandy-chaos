import numpy as np
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT

class CollapseSimulator:
    def __init__(self, center_x=GRID_WIDTH/2, center_y=GRID_HEIGHT/2):
        self.center = np.array([center_x, center_y])
        self.singularity_strength = 800.0
        self.fibre_tension = 5.0
        
    def get_velocity_at(self, x, y, t=0.0):
        """
        Calculates the velocity field for the Entropic Collapse.
        
        Physics:
        1. Singularity Attraction: Nodes are pulled towards the center.
        2. Planar Shear: A rotational component that creates the "intersecting" effect.
        3. Pulse: A breathing rhythm that allows the mesh to expand and contract slightly,
           simulating the "search" for the optimal collapsed state.
        """
        pos = np.array([x, y])
        r_vec = self.center - pos # Vector pointing TO center
        dist = np.linalg.norm(r_vec)
        
        # Prevent division by zero / extreme velocities at singularity
        min_dist = 1.0
        if dist < min_dist:
            dist = min_dist
            
        # 1. Singularity Attraction (Gravity-like)
        # F ~ 1/r, but we want it to be firm but not instant
        attraction_mag = self.singularity_strength / (dist * 1.5)
        v_radial = (r_vec / dist) * attraction_mag
        
        # 2. Planar Shear (Rotation)
        # As things collapse, conservation of angular momentum speeds them up
        # This creates the "twisting" of the fibre
        tangent = np.array([-r_vec[1], r_vec[0]]) / dist
        rotation_mag = (self.singularity_strength * 0.5) / dist
        v_tangent = tangent * rotation_mag
        
        # 3. "Breathing" / Collapse Rhythm
        # The collapse isn't linear; it pulses
        pulse = np.sin(t * 0.5) * 0.2 + 0.8 # oscillates between 0.6 and 1.0
        
        # Combine
        v_total = (v_radial + v_tangent) * pulse
        
        return v_total

    def apply_fibre_binding(self, nodes, mesh):
        """
        Applies 'binding' forces between connected nodes in the mesh.
        This simulates the 'Macro-Fibre' becoming rigid as it forms.
        (This would be called from main.py if we had access to the full mesh here,
         but typically simulations return a field. We'll stick to the field for now
         and let the network/control handle specific node interactions if needed.)
        """
        pass
