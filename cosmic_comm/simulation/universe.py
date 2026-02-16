"""
Simulation Universe Module
==========================
Manages the cosmic simulation: black hole, perturbations, and photon tracing.
"""

import numpy as np
from typing import List, Dict

from cosmic_comm.physics.metric import KerrBlackHole
from cosmic_comm.physics.geodesics import GeodesicTracer
from cosmic_comm.physics.perturbation import MassPerturbation

class CosmicUniverse:
    def __init__(self, M=1.0, a=0.9):
        # Spacetime
        self.black_hole = KerrBlackHole(M, a)
        
        # Perturbations (Obstacles)
        self.perturbations: List[MassPerturbation] = []
        
        # Physics Engine
        self.tracer = GeodesicTracer(self.black_hole, step_size=0.05, perturbations=self.perturbations)
        
    def add_perturbation(self, r, theta, phi, mass=0.1):
        """Add a mass to the universe."""
        p = MassPerturbation(r, theta, phi, mass)
        self.perturbations.append(p)
        # Update tracer reference (though list is mutable, good to be safe)
        self.tracer.perturbations = self.perturbations
        print(f"Added perturbation at r={r:.1f}, phi={phi:.1f}, mass={mass}")
        
    def clear_perturbations(self):
        self.perturbations.clear()
        
    def run_beam_simulation(self, start_x=20.0, width=20.0, rays=40):
        """
        Run a simulation of a parallel beam of photons.
        Returns a list of trajectory dictionaries.
        """
        trajectories = []
        y_range = np.linspace(-width/2, width/2, rays)
        
        for y in y_range:
            # Setup initial state for a beam parallel to x-axis at x=start_x
            r = np.sqrt(start_x**2 + y**2)
            phi = np.arctan2(y, start_x)
            theta = np.pi / 2.0
            
            # Initial momenta (approximate for parallel beam)
            pt = -1.0
            pphi = y 
            ptheta = 0.0
            
            # Solve for pr
            g = self.black_hole.metric_components(r, theta)
            Sigma = g['Sigma']
            Delta = g['Delta']
            sin_theta = np.sin(theta)
            
            g_inv_tt = -((r**2 + self.black_hole.a**2)**2 - Delta * self.black_hole.a**2 * sin_theta**2) / (Delta * Sigma)
            g_inv_tphi = -(2.0 * self.black_hole.M * self.black_hole.a * r) / (Delta * Sigma)
            g_inv_rr = Delta / Sigma
            g_inv_thth = 1.0 / Sigma
            g_inv_phiphi = (Delta - self.black_hole.a**2 * sin_theta**2) / (Delta * Sigma * sin_theta**2)
            
            B = (g_inv_tt * pt**2 + 
                 2 * g_inv_tphi * pt * pphi + 
                 g_inv_thth * ptheta**2 + 
                 g_inv_phiphi * pphi**2)
            A = g_inv_rr
            
            if -B/A >= 0:
                pr = -np.sqrt(-B/A)
                state = np.array([0.0, r, theta, phi, pt, pr, ptheta, pphi])
                traj = self.tracer.trace(state, max_steps=1500)
                trajectories.append(traj)
                
        return trajectories
