"""
Metric Module (Kerr Spacetime)
==============================
This module defines the Kerr metric for a rotating black hole, which describes the
spacetime geometry around the singularity. It provides the equations of motion
(geodesic equations) for light rays (photons) traversing this curved space.

The Kerr metric in Boyer-Lindquist coordinates (t, r, θ, φ) is used here.

References:
- Misner, Thorne & Wheeler (1973), "Gravitation"
- Chandrasekhar (1983), "The Mathematical Theory of Black Holes"
"""

import numpy as np
from dataclasses import dataclass

@dataclass
class KerrBlackHole:
    """Represents a rotating black hole with mass M and spin a."""
    M: float = 1.0          # Mass (G=c=1 units)
    a: float = 0.9          # Spin parameter (J/M), |a| < M
    
    def __post_init__(self):
        # Enforce cosmic censorship (no naked singularities)
        if abs(self.a) > self.M:
            self.a = np.sign(self.a) * self.M * 0.99
            
    def metric_components(self, r, theta):
        """
        Calculate non-zero metric components g_μν at (r, θ).
        Returns a dictionary of components.
        
        Using Boyer-Lindquist coordinates:
        ds² = - (1 - 2Mr/Σ) dt² 
              - (4Mar sin²θ / Σ) dt dφ 
              + (Σ / Δ) dr² 
              + Σ dθ² 
              + ( (r² + a²)² - Δ a² sin²θ ) (sin²θ / Σ) dφ²
        
        Where:
        Σ = r² + a² cos²θ
        Δ = r² - 2Mr + a²
        """
        Sigma = r**2 + (self.a * np.cos(theta))**2
        Delta = r**2 - 2 * self.M * r + self.a**2
        
        sin_theta = np.sin(theta)
        sin2_theta = sin_theta**2
        
        g_tt = -(1.0 - (2.0 * self.M * r) / Sigma)
        g_tphi = -(2.0 * self.M * self.a * r * sin2_theta) / Sigma
        g_rr = Sigma / Delta
        g_thth = Sigma
        g_phiphi = ((r**2 + self.a**2)**2 - Delta * self.a**2 * sin2_theta) * (sin2_theta / Sigma)
        
        return {
            'tt': g_tt,
            'tphi': g_tphi,
            'rr': g_rr,
            'thth': g_thth,
            'phiphi': g_phiphi,
            'Sigma': Sigma,
            'Delta': Delta
        }

    def derivatives(self, state):
        """
        Computes the derivatives [dr/dλ, dθ/dλ, dφ/dλ, dt/dλ] for a photon.
        Instead of solving the full geodesic equation with Christoffel symbols (expensive),
        we use the Constants of Motion approach (Carter's Constant).
        
        State vector: [t, r, theta, phi, k_t, k_r, k_theta, k_phi]
        where k_μ are the covariant components of the 4-momentum (wave vector).
        
        However, for ray tracing, it's often easier to integrate the second-order
        equations directly using the effective potential method, or Hamilton's equations.
        
        We will use the Hamiltonian formulation:
        H = 1/2 g^μν p_μ p_ν = 0 (for photons)
        
        Equations of motion:
        dx^μ/dλ = ∂H/∂p_μ = g^μν p_ν
        dp_μ/dλ = -∂H/∂x^μ = -1/2 (∂g^αβ/∂x^μ) p_α p_β
        """
        t, r, theta, phi = state[:4]
        pt, pr, ptheta, pphi = state[4:] # Covariant momenta p_μ
        
        # Precompute metric functions
        Sigma = r**2 + (self.a * np.cos(theta))**2
        Delta = r**2 - 2 * self.M * r + self.a**2
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        
        # Inverse Metric Components (Contravariant g^μν)
        # These are needed for dx^μ/dλ = g^μν p_ν
        
        # The determinant of the block [[g_tt, g_tphi], [g_tphi, g_phiphi]] is needed
        # But for Kerr, we have analytic inverse forms:
        inv_Sigma = 1.0 / Sigma
        
        g_inv_tt = -((r**2 + self.a**2)**2 - Delta * self.a**2 * sin_theta**2) / (Delta * Sigma)
        g_inv_tphi = -(2.0 * self.M * self.a * r) / (Delta * Sigma)
        g_inv_rr = Delta / Sigma
        g_inv_thth = 1.0 / Sigma
        g_inv_phiphi = (Delta - self.a**2 * sin_theta**2) / (Delta * Sigma * sin_theta**2)
        
        # 1. Velocities (dx^μ/dλ)
        # dt/dλ = g^tt p_t + g^tphi p_phi
        dt = g_inv_tt * pt + g_inv_tphi * pphi
        
        # dr/dλ = g^rr p_r
        dr = g_inv_rr * pr
        
        # dθ/dλ = g^thth p_theta
        dtheta = g_inv_thth * ptheta
        
        # dφ/dλ = g^phit p_t + g^phiphi p_phi
        dphi = g_inv_tphi * pt + g_inv_phiphi * pphi
        
        # 2. Forces (dp_μ/dλ)
        # This requires derivatives of the inverse metric, which is messy.
        # Alternatively, we can use the Separability constants (E, L, Q) if we assume
        # no external forces. BUT, since we want to add PERTURBATIONS later,
        # we should stick to the Hamilton's equations or Geodesic equation form.
        
        # Let's use a numerical approximation for the metric derivatives for flexibility
        # when we add perturbations later.
        
        # For now, let's implement the analytic derivatives for the unperturbed Kerr
        # to ensure stability of the base simulation.
        
        # Derivatives of Sigma and Delta
        dSigma_dr = 2.0 * r
        dSigma_dth = -2.0 * self.a**2 * cos_theta * sin_theta
        dDelta_dr = 2.0 * r - 2.0 * self.M
        
        # We need derivatives of the Hamiltonian H = 0.5 * g^αβ p_α p_β
        # ∂H/∂r = 0.5 * (∂g^αβ/∂r) p_α p_β
        # ∂H/∂θ = 0.5 * (∂g^αβ/∂θ) p_α p_β
        # ∂H/∂t = 0 (Stationary) -> pt is conserved (Energy E)
        # ∂H/∂φ = 0 (Axisymmetric) -> pphi is conserved (Angular Momentum L)
        
        # So dp_t/dλ = 0
        dpt = 0.0
        
        # So dp_phi/dλ = 0
        dpphi = 0.0
        
        # Calculating ∂H/∂r and ∂H/∂θ is tedious but necessary for general orbits
        # For the prototype, we can use a finite difference approximation for these two terms.
        # It's computationally slightly more expensive but much less error-prone to implement.
        
        dH_dr = self._numerical_derivative_H(r, theta, pt, pr, ptheta, pphi, 'r')
        dH_dth = self._numerical_derivative_H(r, theta, pt, pr, ptheta, pphi, 'theta')
        
        dpr = -dH_dr
        dptheta = -dH_dth
        
        return np.array([dt, dr, dtheta, dphi, dpt, dpr, dptheta, dpphi])

    def _numerical_derivative_H(self, r, theta, pt, pr, ptheta, pphi, var, eps=1e-5):
        """
        Computes partial derivative of Hamiltonian w.r.t coordinate using central difference.
        H = 0.5 * g^μν p_μ p_ν
        """
        def get_H(r_val, th_val):
            # Recalculate inverse metric at perturbed coordinates
            Sigma = r_val**2 + (self.a * np.cos(th_val))**2
            Delta = r_val**2 - 2 * self.M * r_val + self.a**2
            sin_th = np.sin(th_val)
            
            # Protect against division by zero at poles
            if abs(sin_th) < 1e-6: sin_th = 1e-6
            
            g_inv_tt = -((r_val**2 + self.a**2)**2 - Delta * self.a**2 * sin_th**2) / (Delta * Sigma)
            g_inv_tphi = -(2.0 * self.M * self.a * r_val) / (Delta * Sigma)
            g_inv_rr = Delta / Sigma
            g_inv_thth = 1.0 / Sigma
            g_inv_phiphi = (Delta - self.a**2 * sin_th**2) / (Delta * Sigma * sin_th**2)
            
            # H = 0.5 * (g^tt pt^2 + 2g^tphi pt pphi + g^rr pr^2 + g^thth pth^2 + g^phiphi pphi^2)
            H = 0.5 * (
                g_inv_tt * pt**2 + 
                2 * g_inv_tphi * pt * pphi + 
                g_inv_rr * pr**2 + 
                g_inv_thth * ptheta**2 + 
                g_inv_phiphi * pphi**2
            )
            return H

        if var == 'r':
            return (get_H(r + eps, theta) - get_H(r - eps, theta)) / (2 * eps)
        elif var == 'theta':
            return (get_H(r, theta + eps) - get_H(r, theta - eps)) / (2 * eps)
        return 0.0
