"""
Tachyonic Loop Module
=====================
Analyzes closed temporal loops for ΔT computation.

When a system trajectory forms a closed loop in physical space, we can
compute the temporal displacement ΔT around that loop. If ΔT ≠ 0, this
indicates a temporal asymmetry - the loop has a "temporal charge" that
could, in principle, enable information to arrive before it was sent.

This module detects, tracks, and analyzes such loops.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import deque


class TachyonicLoop:
    """
    Tracks and analyzes closed loops in phase space for temporal anomalies.
    
    A tachyonic loop is a closed path where:
    ∮ Z(s) ds ≠ 0
    
    This non-zero contour integral indicates temporal displacement.
    """
    
    def __init__(self, max_loops: int = 100):
        """
        Initialize the tachyonic loop tracker.
        
        Args:
            max_loops: Maximum number of loops to retain in history
        """
        self.max_loops = max_loops
        
        # History of detected loops
        self.loop_history = deque(maxlen=max_loops)
        
        # Current loop being tracked
        self.current_loop_path = []
        self.current_loop_states = []
        self.loop_in_progress = False
        self.loop_start_time = 0.0
    
    def start_tracking(self, initial_position: np.ndarray, 
                      initial_state: complex, time: float):
        """
        Begin tracking a potential loop.
        
        Args:
            initial_position: Starting position
            initial_state: Starting complex entropy state
            time: Simulation time
        """
        self.current_loop_path = [initial_position.copy()]
        self.current_loop_states = [initial_state]
        self.loop_in_progress = True
        self.loop_start_time = time
    
    def add_point(self, position: np.ndarray, state: complex):
        """
        Add a point to the current loop being tracked.
        
        Args:
            position: Current position
            state: Current complex entropy state
        """
        if self.loop_in_progress:
            self.current_loop_path.append(position.copy())
            self.current_loop_states.append(state)
    
    def close_loop(self, end_time: float, formalization) -> Optional[Dict]:
        """
        Close the current loop and compute its temporal properties.
        
        Args:
            end_time: Simulation time at loop closure
            formalization: Active formalization for computing ΔT
        
        Returns:
            Dictionary with loop properties, or None if invalid
        """
        if not self.loop_in_progress or len(self.current_loop_path) < 3:
            return None
        
        # Compute temporal displacement
        delta_t = formalization.temporal_displacement(
            self.current_loop_path, 
            self.current_loop_states
        )
        
        # Compute spatial loop properties
        path_array = np.array(self.current_loop_path)
        
        # Loop perimeter
        perimeter = 0.0
        for i in range(len(path_array) - 1):
            perimeter += np.linalg.norm(path_array[i+1] - path_array[i])
        
        # Loop area (Shoelace formula)
        area = 0.0
        for i in range(len(path_array) - 1):
            area += path_array[i, 0] * path_array[i+1, 1]
            area -= path_array[i+1, 0] * path_array[i, 1]
        area = abs(area) / 2.0
        
        # Compute winding number if available
        winding = 0.0
        if hasattr(formalization, 'compute_winding_number'):
            winding = formalization.compute_winding_number(self.current_loop_states)
        
        # Compute average phase and magnitude
        phases = [formalization.get_phase(z) for z in self.current_loop_states]
        magnitudes = [formalization.get_magnitude(z) for z in self.current_loop_states]
        
        loop_data = {
            'start_time': self.loop_start_time,
            'end_time': end_time,
            'duration': end_time - self.loop_start_time,
            'delta_t': delta_t,
            'delta_t_real': delta_t.real,
            'delta_t_imag': delta_t.imag,
            'delta_t_magnitude': abs(delta_t),
            'perimeter': perimeter,
            'area': area,
            'winding_number': winding,
            'avg_phase': np.mean(phases),
            'phase_variance': np.var(phases),
            'avg_magnitude': np.mean(magnitudes),
            'num_points': len(self.current_loop_path),
            'path': self.current_loop_path.copy(),
            'states': self.current_loop_states.copy()
        }
        
        # Add to history
        self.loop_history.append(loop_data)
        
        # Reset current loop
        self.loop_in_progress = False
        self.current_loop_path = []
        self.current_loop_states = []
        
        return loop_data
    
    def detect_and_close_loop(self, positions_history: List[np.ndarray],
                             states_history: List[complex],
                             times_history: List[float],
                             threshold: float,
                             formalization) -> Optional[Dict]:
        """
        Automatically detect and close a loop from position history.
        
        Args:
            positions_history: Recent position history
            states_history: Recent state history
            times_history: Recent time history
            threshold: Distance threshold for loop closure
            formalization: Active formalization
        
        Returns:
            Loop data if detected, None otherwise
        """
        if len(positions_history) < 20:
            return None
        
        current_pos = positions_history[-1]
        
        # Find loop closure point
        for i in range(len(positions_history) - 10):
            past_pos = positions_history[i]
            dist = np.linalg.norm(current_pos - past_pos)
            
            if dist < threshold:
                # Loop detected! Extract it
                loop_path = positions_history[i:]
                loop_states = states_history[i:]
                loop_start_time = times_history[i]
                loop_end_time = times_history[-1]
                
                # Temporarily set as current loop
                self.current_loop_path = loop_path
                self.current_loop_states = loop_states
                self.loop_start_time = loop_start_time
                self.loop_in_progress = True
                
                # Close it
                return self.close_loop(loop_end_time, formalization)
        
        return None
    
    def get_loop_statistics(self) -> Dict[str, float]:
        """
        Get statistics across all detected loops.
        
        Returns:
            Dictionary with aggregate statistics
        """
        if len(self.loop_history) == 0:
            return {
                'num_loops': 0,
                'avg_delta_t_magnitude': 0.0,
                'max_delta_t_magnitude': 0.0,
                'total_winding': 0.0,
                'avg_duration': 0.0
            }
        
        delta_t_mags = [loop['delta_t_magnitude'] for loop in self.loop_history]
        windings = [loop['winding_number'] for loop in self.loop_history]
        durations = [loop['duration'] for loop in self.loop_history]
        
        return {
            'num_loops': len(self.loop_history),
            'avg_delta_t_magnitude': np.mean(delta_t_mags),
            'max_delta_t_magnitude': np.max(delta_t_mags),
            'std_delta_t_magnitude': np.std(delta_t_mags),
            'total_winding': np.sum(windings),
            'avg_winding': np.mean(windings),
            'avg_duration': np.mean(durations),
            'avg_perimeter': np.mean([loop['perimeter'] for loop in self.loop_history]),
            'avg_area': np.mean([loop['area'] for loop in self.loop_history])
        }
    
    def get_recent_loops(self, n: int = 10) -> List[Dict]:
        """
        Get the n most recent loops.
        
        Args:
            n: Number of loops to retrieve
        
        Returns:
            List of loop data dictionaries
        """
        return list(self.loop_history)[-n:]
    
    def has_significant_temporal_anomaly(self, threshold: float = 0.1) -> bool:
        """
        Check if any recent loops show significant temporal displacement.
        
        Args:
            threshold: Threshold for significance
        
        Returns:
            True if anomaly detected
        """
        if len(self.loop_history) == 0:
            return False
        
        # Check most recent loop
        recent = self.loop_history[-1]
        return recent['delta_t_magnitude'] > threshold
