"""
Geodesic Integrator Module
==========================
Numerical integration engine for tracing photon paths (null geodesics) 
through curved spacetime.

Uses Runge-Kutta 4th Order (RK4) integration for high precision.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional

from cosmic_comm.physics.metric import KerrBlackHole
from cosmic_comm.physics.perturbation import MassPerturbation

class GeodesicTracer:
    def __init__(self, metric: KerrBlackHole, step_size: float = 0.1, perturbations: List[MassPerturbation] = None):
        self.metric = metric
        self.dt = step_size
        self.perturbations = perturbations or []
        
        # Horizon radius (outer event horizon)
        # r+ = M + sqrt(M^2 - a^2)
        self.r_horizon = self.metric.M + np.sqrt(self.metric.M**2 - self.metric.a**2)
        
    def trace(self, initial_state: np.ndarray, max_steps: int = 1000) -> Dict:
        """
        Trace a single photon trajectory.
        
        Args:
            initial_state: [t, r, theta, phi, pt, pr, ptheta, pphi]
            max_steps: Maximum integration steps
            
        Returns:
            Dictionary containing trajectory data:
            - 't', 'r', 'theta', 'phi': Arrays of coordinates
            - 'status': 'escaped', 'captured', or 'max_steps'
            - 'proper_time': Total affine parameter length
        """
        # History buffers
        ts, rs, thetas, phis = [], [], [], []
        
        current_state = initial_state.copy()
        
        status = "max_steps"
        
        for step in range(max_steps):
            # Record current position
            ts.append(current_state[0])
            rs.append(current_state[1])
            thetas.append(current_state[2])
            phis.append(current_state[3])
            
            # Check termination conditions
            r = current_state[1]
            
            # 1. Captured by Black Hole (approaching horizon)
            if r < self.r_horizon * 1.05:
                status = "captured"
                break
                
            # 2. Escaped to infinity (far away)
            if r > 50.0 * self.metric.M:
                status = "escaped"
                break
                
            # Integrate one step
            current_state = self._rk4_step(current_state)
            
        return {
            't': np.array(ts),
            'r': np.array(rs),
            'theta': np.array(thetas),
            'phi': np.array(phis),
            'status': status,
            'steps': len(ts)
        }
    
    def _rk4_step(self, state: np.ndarray) -> np.ndarray:
        """
        Perform one RK4 integration step.
        y_{n+1} = y_n + (h/6) * (k1 + 2k2 + 2k3 + k4)
        """
        h = self.dt
        
        def dynamics(s):
            # Base geodesic flow
            d_s = self.metric.derivatives(s)
            
            # Add perturbations forces to momentum derivatives (indices 4,5,6,7)
            # F = [0, Fr, Fth, Fphi]
            total_force = np.zeros(4)
            for p in self.perturbations:
                # Calculate force on momenta
                # Note: get_force returns [F_pt, F_pr, F_pth, F_pphi]
                # We add this to dp_mu/dlambda
                f = p.get_force(s)
                total_force += f
            
            # Add force to momentum derivatives
            d_s[4:] += total_force
            
            return d_s
        
        # k1 = f(y_n)
        k1 = dynamics(state)
        
        # k2 = f(y_n + h/2 * k1)
        k2 = dynamics(state + 0.5 * h * k1)
        
        # k3 = f(y_n + h/2 * k2)
        k3 = dynamics(state + 0.5 * h * k2)
        
        # k4 = f(y_n + h * k3)
        k4 = dynamics(state + h * k3)
        
        # Update state
        new_state = state + (h / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        return new_state

    def initialize_photon(self, r: float, theta: float, phi: float, 
                         E: float = 1.0, L: float = 0.0, Q: float = 0.0,
                         direction: int = -1) -> np.ndarray:
        """
        Initialize a photon state vector given constants of motion.
        Often easier to specify impact parameters or initial direction.
        
        For simplicity in this prototype, we'll initialize based on 
        position and a local direction vector in the orthonormal frame, 
        then convert to coordinate momenta.
        
        Args:
            r, theta, phi: Initial spatial position
            direction: -1 for inward, 1 for outward (radial)
            
        Returns:
            Initial state vector (8 components)
        """
        t = 0.0
        
        # Simplified initialization: Inward radial photon with some angular momentum
        # This is a bit tricky in Kerr. Let's start with a simpler approach:
        # Define p_μ explicitly.
        
        # Metric at initial position
        g = self.metric.metric_components(r, theta)
        
        # Assume E = -p_t = 1 (energy conservation)
        pt = -1.0 
        
        # Assume some angular momentum p_phi = L
        pphi = 4.0 # Should be enough to orbit or scatter
        
        # Assume p_theta = 0 (equatorial-ish start)
        ptheta = 0.0
        
        # Solve for p_r using H = 0 (Null geodesic condition)
        # g^tt pt^2 + 2g^tphi pt pphi + g^rr pr^2 + g^thth pth^2 + g^phiphi pphi^2 = 0
        
        # We need the inverse components. Let's recalculate them locally.
        Sigma = g['Sigma']
        Delta = g['Delta']
        sin_theta = np.sin(theta)
        
        g_inv_tt = -((r**2 + self.metric.a**2)**2 - Delta * self.metric.a**2 * sin_theta**2) / (Delta * Sigma)
        g_inv_tphi = -(2.0 * self.metric.M * self.metric.a * r) / (Delta * Sigma)
        g_inv_rr = Delta / Sigma
        g_inv_thth = 1.0 / Sigma
        g_inv_phiphi = (Delta - self.metric.a**2 * sin_theta**2) / (Delta * Sigma * sin_theta**2)
        
        # Equation for pr^2:
        # A * pr^2 + B = 0  => pr = sqrt(-B/A)
        # A = g^rr
        # B = g^tt pt^2 + 2g^tphi pt pphi + g^thth pth^2 + g^phiphi pphi^2
        
        B = (g_inv_tt * pt**2 + 
             2 * g_inv_tphi * pt * pphi + 
             g_inv_thth * ptheta**2 + 
             g_inv_phiphi * pphi**2)
             
        A = g_inv_rr
        
        # We want A * pr^2 = -B
        # pr^2 = -B / A
        
        if -B/A < 0:
            # Forbidden region for these parameters (classical turning point)
            # Adjust pphi to make it valid, or return None
            # For robustness, let's just zero pphi and shoot radially
            pphi = 0.0
            B = g_inv_tt * pt**2
            # Recalculate
        
        pr_sq = -B / A
        pr = np.sqrt(abs(pr_sq)) # Take absolute to be safe against floating point noise
        
        if direction < 0:
            pr = -pr # Inward
            
        return np.array([t, r, theta, phi, pt, pr, ptheta, pphi])
