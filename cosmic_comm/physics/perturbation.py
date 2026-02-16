"""
Perturbation Module
===================
Models gravitational perturbations (e.g., small masses) that deflect photon paths.
"""

import numpy as np

class MassPerturbation:
    def __init__(
        self,
        r,
        theta,
        phi,
        mass=0.1,
        force_scale: float = 100.0,
        softening: float = 0.1,
        eps: float = 1e-9
    ):
        self.r = r
        self.theta = theta
        self.phi = phi
        self.mass = mass
        self.force_scale = float(force_scale)
        self.softening = float(max(softening, eps))
        self.eps = float(eps)
        
        # Convert to Cartesian for distance calculations (approximation)
        self.pos = self._to_cartesian(r, theta, phi)
        
    def _to_cartesian(self, r, theta, phi):
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return np.array([x, y, z])

    def get_force(self, photon_state):
        """
        Calculate a pseudo-Newtonian force vector in spherical coordinates.
        This is a heuristic approximation to show lensing.
        
        Args:
            photon_state: [t, r, theta, phi, pt, pr, ptheta, pphi]
            
        Returns:
            force_vector: [0, Fr, Ftheta, Fphi] (matching the momenta derivatives)
        """
        r_p, theta_p, phi_p = photon_state[1:4]
        pos_p = self._to_cartesian(r_p, theta_p, phi_p)
        
        # Vector from photon to mass
        diff = self.pos - pos_p
        dist = np.linalg.norm(diff)
        
        if dist < self.softening:
            dist = self.softening
        
        # Force magnitude ~ M/r^2
        # We need to scale this to be visible against the BH gravity
        strength = self.force_scale * self.mass / (dist**2)
        
        # Direction in Cartesian
        f_cart = strength * (diff / dist)
        
        # Project onto spherical basis vectors (approximate)
        # e_r = (sin th cos phi, sin th sin phi, cos th)
        # e_th = (cos th cos phi, cos th sin phi, -sin th)
        # e_phi = (-sin phi, cos phi, 0)
        
        sin_th = np.sin(theta_p)
        cos_th = np.cos(theta_p)
        sin_phi = np.sin(phi_p)
        cos_phi = np.cos(phi_p)
        
        e_r = np.array([sin_th * cos_phi, sin_th * sin_phi, cos_th])
        e_th = np.array([cos_th * cos_phi, cos_th * sin_phi, -sin_th])
        e_phi = np.array([-sin_phi, cos_phi, 0.0])
        
        Fr = np.dot(f_cart, e_r)
        safe_r = max(abs(r_p), self.eps)
        safe_sin = max(abs(sin_th), self.eps)

        Fth = np.dot(f_cart, e_th) / safe_r  # Scale for angular momentum change
        Fphi = np.dot(f_cart, e_phi) / (safe_r * safe_sin) # Scale for angular momentum
        
        # Return force on momenta [pt, pr, ptheta, pphi]
        # pt is energy, usually conserved unless time-dependent potential
        return np.array([0.0, Fr, Fth, Fphi])
