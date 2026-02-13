"""
Euler/Complex Analysis Formalization
=====================================
Implements the complex entropy framework using Euler's identity:
    Z = |S| · e^(iφ)

Where:
- |S| is the entropy magnitude
- φ is the phase angle between order and disorder
- The path integral τ = ∫ Z ds gives emergent time
- Temporal loops exhibit ΔT = τ_forward + τ_backward
"""

import numpy as np
from typing import Dict, List, Any
from .base import Formalization


class EulerFormalization(Formalization):
    """
    Complex analysis formalization using Euler's formula.
    
    Key concepts:
    - Order and disorder as orthogonal dimensions in complex plane
    - Real axis = order, Imaginary axis = disorder
    - Bijection via complex conjugation: Z ↔ Z̄
    - Path integrals yield emergent time with winding number
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Configuration parameters
        self.order_weight = self.config.get('order_weight', 1.0)
        self.disorder_weight = self.config.get('disorder_weight', 1.0)
        self.alignment_threshold = self.config.get('alignment_threshold', 0.1)
    
    def compute_order_parameter(self, state: Dict[str, Any]) -> float:
        """
        Compute order parameter from velocity alignment and mesh regularity.
        
        High order = velocities aligned, mesh regular (low shear/gradient variance)
        
        Args:
            state: Must contain 'velocities' and optionally 'gradients'
        
        Returns:
            Order parameter in [0, 1]
        """
        velocities = state.get('velocities', np.array([]))
        gradients = state.get('gradients', [])
        
        if len(velocities) == 0:
            return 0.0
        
        # 1. Velocity Alignment (Order Metric)
        # How aligned are the velocity vectors?
        speeds = np.linalg.norm(velocities, axis=1)
        non_zero = speeds > 1e-6
        
        if np.sum(non_zero) < 2:
            alignment = 0.0
        else:
            # Normalize velocities
            normalized = velocities[non_zero] / speeds[non_zero, np.newaxis]
            # Average direction
            mean_direction = np.mean(normalized, axis=0)
            mean_alignment = np.linalg.norm(mean_direction)
            alignment = mean_alignment  # Close to 1 = all aligned
        
        # 2. Mesh Regularity (Structural Order)
        if len(gradients) > 0:
            grad_values = np.array([g['gradient'] for g in gradients])
            # Low variance in gradients = regular structure
            grad_std = np.std(grad_values)
            regularity = 1.0 / (1.0 + grad_std)  # High when std is low
        else:
            regularity = 0.5  # Neutral
        
        # Combine metrics
        order = 0.6 * alignment + 0.4 * regularity
        return np.clip(order, 0.0, 1.0)
    
    def compute_disorder_parameter(self, state: Dict[str, Any]) -> float:
        """
        Compute disorder parameter from velocity variance and shear intensity.
        
        High disorder = velocities scattered, high shear (turbulence)
        
        Args:
            state: Must contain 'velocities' and optionally 'gradients'
        
        Returns:
            Disorder parameter in [0, 1]
        """
        velocities = state.get('velocities', np.array([]))
        gradients = state.get('gradients', [])
        
        if len(velocities) == 0:
            return 0.0
        
        # 1. Velocity Variance (Chaos Metric)
        speeds = np.linalg.norm(velocities, axis=1)
        if len(speeds) > 1:
            speed_variance = np.var(speeds) / (np.mean(speeds) + 1e-6)**2
            variance_metric = np.tanh(speed_variance)  # Saturate to [0, 1]
        else:
            variance_metric = 0.0
        
        # 2. Shear Intensity (Turbulence)
        if len(gradients) > 0:
            grad_values = np.array([g['gradient'] for g in gradients])
            mean_shear = np.mean(grad_values)
            shear_metric = np.tanh(mean_shear / 10.0)  # Normalize
        else:
            shear_metric = 0.0
        
        # Combine metrics
        disorder = 0.5 * variance_metric + 0.5 * shear_metric
        return np.clip(disorder, 0.0, 1.0)
    
    def bijection(self, alpha: float) -> float:
        """
        Bijection: Order ↔ Disorder
        
        Simple reflection: β = 1 - α
        (Could also implement as β = α for symmetric pairing, or β = 1/α for inversion)
        
        Args:
            alpha: Order parameter
        
        Returns:
            Disorder parameter beta
        """
        # Reflection: maximum disorder when minimum order
        return 1.0 - alpha
    
    def complex_entropy_state(self, alpha: float, beta: float) -> complex:
        """
        Construct complex entropy state: Z = |S| · e^(iφ)
        
        |S| = magnitude from combined entropy
        φ = phase angle from order/disorder ratio
        
        Args:
            alpha: Order parameter (real axis component)
            beta: Disorder parameter (imaginary axis component)
        
        Returns:
            Complex entropy state Z
        """
        # Magnitude: Euclidean norm of (alpha, beta) vector
        magnitude = np.sqrt(alpha**2 + beta**2)
        
        # Phase: arctan2 gives angle from order to disorder
        # φ = 0 when pure order (α=1, β=0)
        # φ = π/2 when pure disorder (α=0, β=1)
        phase = np.arctan2(beta, alpha)
        
        # Euler form: Z = |S| · e^(iφ)
        z = magnitude * np.exp(1j * phase)
        
        return z
    
    def path_integral(self, path: List[np.ndarray], states: List[complex]) -> complex:
        """
        Compute emergent time: τ = ∫_γ Z(s) ds
        
        Path integral of complex entropy states along a path.
        
        Args:
            path: List of position vectors [p0, p1, ..., pN]
            states: List of complex entropy states [Z0, Z1, ..., ZN]
        
        Returns:
            Complex emergent time τ
        """
        if len(path) < 2 or len(states) < 2:
            return 0.0 + 0.0j
        
        tau = 0.0 + 0.0j
        
        # Trapezoidal integration along path
        for i in range(len(path) - 1):
            # Path segment length
            ds = np.linalg.norm(path[i+1] - path[i])
            
            # Average entropy state over segment
            z_avg = (states[i] + states[i+1]) / 2.0
            
            # Integrate: τ += Z(s) · ds
            tau += z_avg * ds
        
        return tau
    
    def temporal_displacement(self, loop_path: List[np.ndarray], 
                            loop_states: List[complex]) -> complex:
        """
        Compute temporal displacement ΔT for closed loop.
        
        ΔT = ∮ Z(s) ds  (contour integral around loop)
        
        If ΔT ≠ 0, there's a temporal asymmetry (potential tachyonic behavior)
        
        Args:
            loop_path: Closed loop of positions (first and last should be same/close)
            loop_states: Complex entropy states around loop
        
        Returns:
            Complex temporal displacement ΔT
        """
        # Ensure loop is closed
        if len(loop_path) < 3:
            return 0.0 + 0.0j
        
        # Compute contour integral
        delta_t = self.path_integral(loop_path, loop_states)
        
        return delta_t
    
    def get_phase(self, z: complex) -> float:
        """
        Extract phase angle from complex entropy state.
        
        Args:
            z: Complex entropy state
        
        Returns:
            Phase angle φ in radians [-π, π]
        """
        return np.angle(z)
    
    def get_magnitude(self, z: complex) -> float:
        """
        Extract magnitude from complex entropy state.
        
        Args:
            z: Complex entropy state
        
        Returns:
            Magnitude |S|
        """
        return np.abs(z)
    
    def compute_winding_number(self, loop_states: List[complex]) -> float:
        """
        Compute the winding number of a closed loop in complex plane.
        
        Winding number n = (1/2π) ∮ dφ
        
        Args:
            loop_states: Complex entropy states around closed loop
        
        Returns:
            Winding number (integer for true closed loops, float for approximate)
        """
        if len(loop_states) < 3:
            return 0.0
        
        # Compute phase change around loop
        phases = [self.get_phase(z) for z in loop_states]
        
        # Accumulate phase change (handling 2π wrapping)
        total_phase_change = 0.0
        for i in range(len(phases) - 1):
            delta_phi = phases[i+1] - phases[i]
            
            # Unwrap: if jump > π, we crossed the branch cut
            if delta_phi > np.pi:
                delta_phi -= 2 * np.pi
            elif delta_phi < -np.pi:
                delta_phi += 2 * np.pi
            
            total_phase_change += delta_phi
        
        # Winding number
        winding = total_phase_change / (2 * np.pi)
        
        return winding
