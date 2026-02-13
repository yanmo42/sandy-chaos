"""
Duality Space Module
====================
Manages the order-disorder bijection and complex entropy state computation.

This module uses the active formalization (from the plugin system) to:
1. Compute order parameter Ω from system state
2. Compute disorder parameter Ω̄ via bijection
3. Construct complex entropy states Z = |S| · e^(iφ)
4. Track path integrals for emergent time τ
5. Maintain history for temporal analysis

The Duality Space is where the "third thing" (the interaction between order
and disorder) manifests as a complex-valued field that evolves in time.
"""

import numpy as np
from typing import List, Dict, Tuple, Any
from collections import deque
from nfem_suite.formalization import registry


class DualitySpace:
    """
    Manages the dual order-disorder space and complex entropy states.
    
    This is the conceptual space where order and disorder parameters
    coexist and interact, giving rise to emergent temporal phenomena.
    """
    
    def __init__(self, history_length: int = 1000):
        """
        Initialize the duality space.
        
        Args:
            history_length: Number of timesteps to retain in history
        """
        self.history_length = history_length
        
        # Current state
        self.current_order = 0.0
        self.current_disorder = 0.0
        self.current_complex_state = 0.0 + 0.0j
        self.current_phase = 0.0
        self.current_magnitude = 0.0
        
        # History tracking for path integrals
        self.order_history = deque(maxlen=history_length)
        self.disorder_history = deque(maxlen=history_length)
        self.complex_state_history = deque(maxlen=history_length)
        self.position_history = deque(maxlen=history_length)  # Centroid positions
        self.time_history = deque(maxlen=history_length)
        
        # Emergent time tracking
        self.emergent_time = 0.0 + 0.0j
        self.emergent_time_history = deque(maxlen=history_length)
        
        # Winding number tracking
        self.winding_number = 0.0
        self.winding_history = deque(maxlen=history_length)
    
    def update(self, positions: np.ndarray, velocities: np.ndarray, 
               gradients: List[Dict], sim_time: float):
        """
        Update the duality space based on current system state.
        
        Args:
            positions: Node positions (N x 2)
            velocities: Node velocities (N x 2)
            gradients: Velocity gradient data from vector space
            sim_time: Current simulation time
        """
        # Get active formalization
        formalization = registry.get_active()
        
        # Prepare state dictionary
        state = {
            'positions': positions,
            'velocities': velocities,
            'gradients': gradients
        }
        
        # Compute order and disorder parameters
        self.current_order = formalization.compute_order_parameter(state)
        self.current_disorder = formalization.compute_disorder_parameter(state)
        
        # Construct complex entropy state
        self.current_complex_state = formalization.complex_entropy_state(
            self.current_order, self.current_disorder
        )
        
        # Extract phase and magnitude
        self.current_phase = formalization.get_phase(self.current_complex_state)
        self.current_magnitude = formalization.get_magnitude(self.current_complex_state)
        
        # Compute system centroid for path tracking
        if len(positions) > 0:
            centroid = np.mean(positions, axis=0)
        else:
            centroid = np.array([0.0, 0.0])
        
        # Update history
        self.order_history.append(self.current_order)
        self.disorder_history.append(self.current_disorder)
        self.complex_state_history.append(self.current_complex_state)
        self.position_history.append(centroid)
        self.time_history.append(sim_time)
        
        # Compute path integral for emergent time (if we have history)
        if len(self.position_history) >= 2:
            # Take last N points for integration
            path_window = min(100, len(self.position_history))
            path = list(self.position_history)[-path_window:]
            states = list(self.complex_state_history)[-path_window:]
            
            tau = formalization.path_integral(path, states)
            self.emergent_time = tau
            self.emergent_time_history.append(tau)
        
        # Compute winding number if we have enough history
        if len(self.complex_state_history) >= 10:
            # Use recent history for winding
            recent_states = list(self.complex_state_history)[-50:]
            
            # Check if EulerFormalization (has compute_winding_number method)
            if hasattr(formalization, 'compute_winding_number'):
                self.winding_number = formalization.compute_winding_number(recent_states)
                self.winding_history.append(self.winding_number)
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current duality space state.
        
        Returns:
            Dictionary with current order, disorder, complex state, etc.
        """
        return {
            'order': self.current_order,
            'disorder': self.current_disorder,
            'complex_state': self.current_complex_state,
            'phase': self.current_phase,
            'magnitude': self.current_magnitude,
            'emergent_time': self.emergent_time,
            'emergent_time_real': self.emergent_time.real,
            'emergent_time_imag': self.emergent_time.imag,
            'winding_number': self.winding_number
        }
    
    def get_history_arrays(self) -> Dict[str, np.ndarray]:
        """
        Get history data as numpy arrays for plotting.
        
        Returns:
            Dictionary with history arrays
        """
        return {
            'time': np.array(list(self.time_history)),
            'order': np.array(list(self.order_history)),
            'disorder': np.array(list(self.disorder_history)),
            'phase': np.array([np.angle(z) for z in self.complex_state_history]),
            'magnitude': np.array([np.abs(z) for z in self.complex_state_history]),
            'emergent_time_real': np.array([tau.real for tau in self.emergent_time_history]),
            'emergent_time_imag': np.array([tau.imag for tau in self.emergent_time_history]),
            'winding': np.array(list(self.winding_history))
        }
    
    def detect_loop(self, threshold: float = 5.0) -> bool:
        """
        Detect if the system has completed a closed loop in phase space.
        
        Args:
            threshold: Distance threshold for loop closure
        
        Returns:
            True if loop detected, False otherwise
        """
        if len(self.position_history) < 20:
            return False
        
        # Check if current position is close to an earlier position
        current_pos = self.position_history[-1]
        
        # Look back in history (skip very recent positions)
        for i in range(len(self.position_history) - 10):
            past_pos = self.position_history[i]
            dist = np.linalg.norm(current_pos - past_pos)
            
            if dist < threshold:
                return True
        
        return False
    
    def get_loop_segment(self, threshold: float = 5.0) -> Tuple[List[np.ndarray], List[complex]]:
        """
        Extract the most recent closed loop (if one exists).
        
        Args:
            threshold: Distance threshold for loop closure
        
        Returns:
            Tuple of (path, states) for the loop, or ([], []) if no loop
        """
        if len(self.position_history) < 20:
            return [], []
        
        current_pos = self.position_history[-1]
        
        # Find the earliest position that closes the loop
        loop_start_idx = -1
        for i in range(len(self.position_history) - 10):
            past_pos = self.position_history[i]
            dist = np.linalg.norm(current_pos - past_pos)
            
            if dist < threshold:
                loop_start_idx = i
                break
        
        if loop_start_idx == -1:
            return [], []
        
        # Extract loop segment
        loop_path = list(self.position_history)[loop_start_idx:]
        loop_states = list(self.complex_state_history)[loop_start_idx:]
        
        return loop_path, loop_states
    
    def compute_temporal_displacement(self, threshold: float = 5.0) -> complex:
        """
        Compute ΔT for the most recent closed loop (if exists).
        
        Args:
            threshold: Distance threshold for loop closure
        
        Returns:
            Complex temporal displacement ΔT, or 0 if no loop
        """
        loop_path, loop_states = self.get_loop_segment(threshold)
        
        if len(loop_path) < 3:
            return 0.0 + 0.0j
        
        formalization = registry.get_active()
        delta_t = formalization.temporal_displacement(loop_path, loop_states)
        
        return delta_t
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Get statistical summary of duality space.
        
        Returns:
            Dictionary with statistics
        """
        if len(self.order_history) == 0:
            return {
                'mean_order': 0.0,
                'mean_disorder': 0.0,
                'mean_phase': 0.0,
                'mean_magnitude': 0.0,
                'phase_variance': 0.0,
                'winding_rate': 0.0
            }
        
        order_arr = np.array(list(self.order_history))
        disorder_arr = np.array(list(self.disorder_history))
        phase_arr = np.array([np.angle(z) for z in self.complex_state_history])
        magnitude_arr = np.array([np.abs(z) for z in self.complex_state_history])
        
        # Winding rate (change in winding number per unit time)
        if len(self.winding_history) > 1 and len(self.time_history) > 1:
            time_span = self.time_history[-1] - self.time_history[max(0, len(self.time_history) - len(self.winding_history))]
            winding_change = abs(self.winding_history[-1] - self.winding_history[0])
            winding_rate = winding_change / max(time_span, 1e-6)
        else:
            winding_rate = 0.0
        
        return {
            'mean_order': np.mean(order_arr),
            'std_order': np.std(order_arr),
            'mean_disorder': np.mean(disorder_arr),
            'std_disorder': np.std(disorder_arr),
            'mean_phase': np.mean(phase_arr),
            'phase_variance': np.var(phase_arr),
            'mean_magnitude': np.mean(magnitude_arr),
            'current_winding': self.winding_number,
            'winding_rate': winding_rate,
            'emergent_time_magnitude': abs(self.emergent_time)
        }
    
    def reset(self):
        """Reset the duality space to initial state."""
        self.order_history.clear()
        self.disorder_history.clear()
        self.complex_state_history.clear()
        self.position_history.clear()
        self.time_history.clear()
        self.emergent_time_history.clear()
        self.winding_history.clear()
        
        self.current_order = 0.0
        self.current_disorder = 0.0
        self.current_complex_state = 0.0 + 0.0j
        self.emergent_time = 0.0 + 0.0j
        self.winding_number = 0.0
