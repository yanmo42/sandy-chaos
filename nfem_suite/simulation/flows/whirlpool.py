import numpy as np
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT

class WhirlpoolSimulator:
    def __init__(self, center_x=GRID_WIDTH/2, center_y=GRID_HEIGHT/2, strength=500.0):
        self.center = np.array([center_x, center_y])
        self.strength = strength
        self.radius = 10.0 # Core radius
        
        # Chaos Parameters (Folding)
        self.perturbation_freq = 0.5
        self.perturbation_amp = 2.0

    def get_velocity_at(self, x, y, t=0.0):
        """
        Returns the velocity vector (vx, vy) at position (x, y).
        Combines a Rankine Vortex with a Time-Dependent Shear Flow
        to create chaotic folding patterns near the center.
        """
        pos = np.array([x, y])
        r_vec = pos - self.center
        r = np.linalg.norm(r_vec)
        
        # Prevent singularity
        if r < 0.1:
            r = 0.1

        # 1. Base Vortex (Rankine)
        if r < self.radius:
            v_mag = (self.strength * r) / (2 * np.pi * self.radius**2)
        else:
            v_mag = self.strength / (2 * np.pi * r)

        tangent = np.array([-r_vec[1], r_vec[0]]) / r
        radial_suction = -0.1 * v_mag * (r_vec / r)
        
        v_vortex = (tangent * v_mag) + radial_suction
        
        # 2. Perturbation Field (The "Folding")
        # Creating a time-dependent saddle point or shear
        # u = A * sin(wt) * x
        # v = -A * sin(wt) * y
        # This creates stretching in one direction and compression in the other -> Folding
        
        # Shift coords to center for perturbation
        local_x = r_vec[0]
        local_y = r_vec[1]
        
        phase = t * self.perturbation_freq
        
        # Rotating saddle point
        c = np.cos(phase)
        s = np.sin(phase)
        
        # Rotate the perturbation axis
        p_x = local_x * c - local_y * s
        p_y = local_x * s + local_y * c
        
        v_perturb_x = self.perturbation_amp * np.sin(phase) * p_y
        v_perturb_y = self.perturbation_amp * np.sin(phase) * p_x # Simple shear
        
        v_perturb = np.array([v_perturb_x, v_perturb_y])
        
        return v_vortex + v_perturb
