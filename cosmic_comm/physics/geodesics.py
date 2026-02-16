"""
Geodesic Integrator Module
==========================
Numerical integration engine for tracing photon paths (null geodesics) 
through curved spacetime.

Uses Runge-Kutta 4th Order (RK4) integration for high precision.
"""

import numpy as np
from typing import List, Dict

from cosmic_comm.physics.metric import KerrBlackHole
from cosmic_comm.physics.perturbation import MassPerturbation

class GeodesicTracer:
    def __init__(
        self,
        metric: KerrBlackHole,
        step_size: float = 0.1,
        perturbations: List[MassPerturbation] = None,
        null_tolerance: float = 1e-2,
        max_radius_factor: float = 50.0,
        capture_margin: float = 1.05
    ):
        self.metric = metric
        self.dt = step_size
        self.perturbations = perturbations or []
        self.null_tolerance = float(null_tolerance)
        self.max_radius_factor = float(max_radius_factor)
        self.capture_margin = float(capture_margin)
        
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
        null_errors = []
        
        current_state = initial_state.copy()
        
        status = "max_steps"
        max_null_error = 0.0
        constraint_violated = False
        
        for step in range(max_steps):
            if not np.all(np.isfinite(current_state)):
                status = "numerical_error"
                break

            # Record current position
            ts.append(current_state[0])
            rs.append(current_state[1])
            thetas.append(current_state[2])
            phis.append(current_state[3])

            null_error = abs(self.metric.null_constraint(current_state))
            null_errors.append(null_error)
            if np.isfinite(null_error):
                max_null_error = max(max_null_error, float(null_error))
            if null_error > self.null_tolerance:
                constraint_violated = True
            
            # Check termination conditions
            r = current_state[1]
            
            # 1. Captured by Black Hole (approaching horizon)
            if r < self.r_horizon * self.capture_margin:
                status = "captured"
                break
                
            # 2. Escaped to infinity (far away)
            if r > self.max_radius_factor * self.metric.M:
                status = "escaped"
                break
                
            # Integrate one step
            current_state = self._rk4_step(current_state)

        if constraint_violated and status == "max_steps":
            status = "constraint_warning"

        proper_time = len(ts) * self.dt
        mean_null_error = float(np.mean(null_errors)) if null_errors else np.nan
        initial_null_error = float(null_errors[0]) if null_errors else np.nan
        final_null_error = float(null_errors[-1]) if null_errors else np.nan
            
        return {
            't': np.array(ts),
            'r': np.array(rs),
            'theta': np.array(thetas),
            'phi': np.array(phis),
            'status': status,
            'steps': len(ts),
            'proper_time': proper_time,
            'null_constraint': np.array(null_errors),
            'initial_null_error': initial_null_error,
            'final_null_error': final_null_error,
            'mean_null_error': mean_null_error,
            'max_null_error': float(max_null_error),
            'constraint_violated': bool(constraint_violated)
        }
    
    def _rk4_step(self, state: np.ndarray) -> np.ndarray:
        """
        Perform one RK4 integration step.
        y_{n+1} = y_n + (h/6) * (k1 + 2k2 + 2k3 + k4)
        """
        h = self.dt

        if not np.all(np.isfinite(state)):
            return np.full_like(state, np.nan, dtype=float)
        
        def dynamics(s):
            if not np.all(np.isfinite(s)):
                return np.full_like(s, np.nan, dtype=float)

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

        if not (np.all(np.isfinite(k1)) and np.all(np.isfinite(k2)) and np.all(np.isfinite(k3)) and np.all(np.isfinite(k4))):
            return np.full_like(state, np.nan, dtype=float)
        
        # Update state
        new_state = state + (h / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

        if not np.all(np.isfinite(new_state)):
            return np.full_like(state, np.nan, dtype=float)
        
        return new_state.astype(float)

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
        
        # Assume E = -p_t > 0 (energy conservation)
        pt = -abs(E)
        
        # Assume some angular momentum p_phi = L
        pphi = float(L) if L != 0.0 else 4.0 # Should be enough to orbit or scatter
        
        # Assume p_theta = 0 (equatorial-ish start)
        ptheta = 0.0
        
        # Solve for p_r using H = 0 (Null geodesic condition)
        # g^tt pt^2 + 2g^tphi pt pphi + g^rr pr^2 + g^thth pth^2 + g^phiphi pphi^2 = 0
        
        # We need the inverse components. Let's recalculate them locally.
        g_inv = self.metric.inverse_metric_components(r, theta)
        
        # Equation for pr^2:
        # A * pr^2 + B = 0  => pr = sqrt(-B/A)
        # A = g^rr
        # B = g^tt pt^2 + 2g^tphi pt pphi + g^thth pth^2 + g^phiphi pphi^2
        
        B = (
            g_inv['tt'] * pt**2 +
            2 * g_inv['tphi'] * pt * pphi +
            g_inv['thth'] * ptheta**2 +
            g_inv['phiphi'] * pphi**2
        )
             
        A = g_inv['rr']

        if abs(A) < 1e-12:
            raise ValueError("Unable to initialize photon: near-singular radial metric component.")
        
        # We want A * pr^2 = -B
        # pr^2 = -B / A
        
        if -B/A < 0:
            # Forbidden region for these parameters (classical turning point)
            # Adjust pphi to make it valid, or return None
            # For robustness, let's just zero pphi and shoot radially
            pphi = 0.0
            B = g_inv['tt'] * pt**2
            # Recalculate
        
        pr_sq = -B / A
        if pr_sq < -1e-10:
            raise ValueError("Unable to initialize photon: null-condition gives negative pr^2.")
        pr = np.sqrt(max(pr_sq, 0.0))
        
        if direction < 0:
            pr = -pr # Inward
            
        return np.array([t, r, theta, phi, pt, pr, ptheta, pphi], dtype=float)
