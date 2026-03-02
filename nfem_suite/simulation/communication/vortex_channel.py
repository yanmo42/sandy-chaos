"""
Vortex Channel Module
=====================
Simulates bidirectional A↔B communication through a vortex mediator.

The vortex acts as a "transceiver" that couples upstream and downstream
perturbations, enabling information flow in both directions:

1. Forward path (A → Vortex → B): Information propagates with the flow
2. Backward path (B → Vortex → A): Information propagates via pressure waves,
   back-eddies, and frame-dragging effects

The key insight: the vortex's rotational structure creates pathways for
backward influence, similar to how a black hole's ergosphere allows
retrograde orbits.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Sequence
from collections import deque


class VortexChannel:
    """
    Models A↔B bidirectional communication through a vortex mediator.
    
    The vortex at position V mediates between:
    - Source A (upstream perturbation source)
    - Receiver B (downstream receiver)
    
    Both can send and receive through the vortex.
    """
    
    def __init__(self, vortex_center: np.ndarray, vortex_radius: float,
                 coupling_strength: float = 1.0,
                 backward_attenuation: float = 0.5):
        """
        Initialize the vortex communication channel.
        
        Args:
            vortex_center: Position of vortex center
            vortex_radius: Effective radius of vortex influence
            coupling_strength: How strongly the vortex couples A and B
            backward_attenuation: Multiplicative loss on B→A path (1.0 = null symmetric model)
        """
        self.vortex_center = vortex_center.copy()
        self.vortex_radius = vortex_radius
        self.coupling_strength = coupling_strength
        self.backward_attenuation = float(backward_attenuation)
        
        # Source A (upstream)
        self.source_a_position = None
        self.source_a_signal_history = deque(maxlen=1000)
        
        # Receiver B (downstream)  
        self.receiver_b_position = None
        self.receiver_b_signal_history = deque(maxlen=1000)
        
        # Channel state
        self.vortex_state = 0.0  # Accumulated perturbation in vortex
        self.forward_transmission_history = deque(maxlen=1000)
        self.backward_transmission_history = deque(maxlen=1000)
        
        # Propagation delays (in timesteps)
        self.forward_delay = 5
        self.backward_delay = 8  # Longer due to indirect propagation
        
        # Buffers for delayed transmission
        self.forward_buffer = deque(maxlen=100)
        self.backward_buffer = deque(maxlen=100)
        
        # Statistics
        self.total_forward_bits = 0.0
        self.total_backward_bits = 0.0
        self.channel_capacity_estimate = 0.0
    
    def set_source_a(self, position: np.ndarray):
        """Set position of source A (upstream)."""
        self.source_a_position = position.copy()
    
    def set_receiver_b(self, position: np.ndarray):
        """Set position of receiver B (downstream)."""
        self.receiver_b_position = position.copy()
    
    def inject_signal_at_a(self, signal: float, time: float):
        """
        Inject a signal at source A.
        
        Args:
            signal: Signal value (float, can represent information)
            time: Current simulation time
        """
        self.source_a_signal_history.append({'signal': signal, 'time': time})
        
        # Add to forward transmission buffer with delay
        self.forward_buffer.append({
            'signal': signal,
            'time': time,
            'arrival_time': time + self.forward_delay * 0.1  # Convert delay to sim time
        })
    
    def inject_signal_at_b(self, signal: float, time: float):
        """
        Inject a signal at receiver B (which can also transmit backward).
        
        Args:
            signal: Signal value
            time: Current simulation time
        """
        self.receiver_b_signal_history.append({'signal': signal, 'time': time})
        
        # Add to backward transmission buffer
        self.backward_buffer.append({
            'signal': signal,
            'time': time,
            'arrival_time': time + self.backward_delay * 0.1
        })
    
    def update(self, current_time: float, flow_field: Optional[callable] = None):
        """
        Update the vortex channel state.
        
        Args:
            current_time: Current simulation time
            flow_field: Optional function(x, y, t) -> velocity for advection
        """
        # Update vortex state with accumulated perturbations
        # The vortex "rings" with the signals passing through it
        decay = 0.95
        self.vortex_state *= decay
        
        # Process forward transmissions (A → B)
        forward_received = []
        while len(self.forward_buffer) > 0:
            packet = self.forward_buffer[0]
            if packet['arrival_time'] <= current_time:
                self.forward_buffer.popleft()
                
                # Signal arrives at B
                # Apply vortex coupling (signal may be amplified/modified)
                coupling_factor = self._compute_coupling_factor(
                    self.source_a_position, 
                    self.receiver_b_position
                )
                
                received_signal = packet['signal'] * coupling_factor
                forward_received.append(received_signal)
                
                # Update vortex state
                self.vortex_state += abs(received_signal) * 0.1
                
                # Record transmission
                self.forward_transmission_history.append({
                    'sent_time': packet['time'],
                    'received_time': current_time,
                    'delay': current_time - packet['time'],
                    'signal': received_signal
                })
                
                self.total_forward_bits += abs(received_signal)
            else:
                break
        
        # Process backward transmissions (B → A)
        backward_received = []
        while len(self.backward_buffer) > 0:
            packet = self.backward_buffer[0]
            if packet['arrival_time'] <= current_time:
                self.backward_buffer.popleft()
                
                # Signal arrives at A (backward propagation!)
                coupling_factor = self._compute_coupling_factor(
                    self.receiver_b_position,
                    self.source_a_position
                )
                
                # Backward transmission can be attenuated relative to forward path.
                # Set backward_attenuation=1.0 for a symmetric null model.
                received_signal = packet['signal'] * coupling_factor * self.backward_attenuation
                backward_received.append(received_signal)
                
                # Update vortex state
                self.vortex_state += abs(received_signal) * 0.1
                
                # Record transmission
                self.backward_transmission_history.append({
                    'sent_time': packet['time'],
                    'received_time': current_time,
                    'delay': current_time - packet['time'],
                    'signal': received_signal
                })
                
                self.total_backward_bits += abs(received_signal)
            else:
                break
        
        # Estimate channel capacity
        if len(self.forward_transmission_history) > 10:
            recent_forward = list(self.forward_transmission_history)[-100:]
            time_span = recent_forward[-1]['received_time'] - recent_forward[0]['sent_time']
            if time_span > 0:
                bits_transmitted = sum(abs(t['signal']) for t in recent_forward)
                self.channel_capacity_estimate = bits_transmitted / time_span
    
    def _compute_coupling_factor(self, from_pos: np.ndarray, 
                                 to_pos: np.ndarray) -> float:
        """
        Compute how strongly the vortex couples two positions.
        
        Args:
            from_pos: Source position
            to_pos: Destination position
        
        Returns:
            Coupling factor in [0, 1]
        """
        if from_pos is None or to_pos is None:
            return 0.0
        
        # Distance from source to vortex
        dist_from = np.linalg.norm(from_pos - self.vortex_center)
        
        # Distance from vortex to destination
        dist_to = np.linalg.norm(to_pos - self.vortex_center)
        
        # Both should be within vortex influence
        influence_from = np.exp(-dist_from / self.vortex_radius)
        influence_to = np.exp(-dist_to / self.vortex_radius)
        
        # Coupling is geometric mean
        coupling = np.sqrt(influence_from * influence_to) * self.coupling_strength
        
        return coupling
    
    def get_forward_channel_quality(self) -> float:
        """
        Measure forward channel quality (A → B).
        
        Returns:
            Quality metric in [0, 1]
        """
        if len(self.forward_transmission_history) < 5:
            return 0.0
        
        recent = list(self.forward_transmission_history)[-50:]
        
        # Quality based on signal strength and consistency
        signals = [abs(t['signal']) for t in recent]
        avg_signal = np.mean(signals)
        std_signal = np.std(signals)
        
        # Good quality = high signal, low variance
        quality = avg_signal / (1.0 + std_signal)
        
        return min(quality, 1.0)
    
    def get_backward_channel_quality(self) -> float:
        """
        Measure backward channel quality (B → A).
        
        Returns:
            Quality metric in [0, 1]
        """
        if len(self.backward_transmission_history) < 5:
            return 0.0
        
        recent = list(self.backward_transmission_history)[-50:]
        
        signals = [abs(t['signal']) for t in recent]
        avg_signal = np.mean(signals)
        std_signal = np.std(signals)
        
        quality = avg_signal / (1.0 + std_signal)
        
        return min(quality, 1.0)
    
    def compute_mutual_information(self) -> float:
        """
        Estimate mutual information between A and B.
        
        This measures how much information successfully travels through
        the vortex channel.
        
        Returns:
            Mutual information estimate (bits)
        """
        if len(self.forward_transmission_history) < 10:
            return 0.0
        
        # Simple estimate based on correlation between sent and received
        recent_forward = list(self.forward_transmission_history)[-100:]
        
        signals = [abs(t['signal']) for t in recent_forward]
        
        # If signals are getting through, MI is high
        # This is a simplified estimate
        mi = np.mean(signals) * np.log2(1.0 + np.var(signals))
        
        return mi
    
    @staticmethod
    def _aggregate_directional_communication(transmissions: List[Dict[str, float]],
                                             delta_tau_bins: np.ndarray) -> np.ndarray:
        """Estimate C(Δτ) from delivered transmissions in a strictly causal way.

        Only packets with positive propagation delay contribute. This enforces
        forward causality: no packet can contribute at Δτ <= 0.
        """
        if len(delta_tau_bins) < 2:
            raise ValueError("delta_tau_bins must contain at least two bin edges")

        profile = np.zeros(len(delta_tau_bins) - 1, dtype=float)
        counts = np.zeros(len(delta_tau_bins) - 1, dtype=float)

        for tx in transmissions:
            delta_tau = float(tx.get('delay', tx['received_time'] - tx['sent_time']))
            if delta_tau <= 0.0:
                continue
            bin_idx = int(np.searchsorted(delta_tau_bins, delta_tau, side='right') - 1)
            if 0 <= bin_idx < len(profile):
                profile[bin_idx] += abs(float(tx['signal']))
                counts[bin_idx] += 1.0

        nz = counts > 0
        profile[nz] = profile[nz] / counts[nz]
        return profile

    def compute_temporal_frame_metrics(self,
                                       delta_tau_bins: Optional[Sequence[float]] = None,
                                       coupling_values: Optional[Sequence[float]] = None) -> Dict[str, np.ndarray]:
        """Compute directional communication profiles C_A→B(Δτ), C_B→A(Δτ), and asymmetry.

        Args:
            delta_tau_bins: Optional bin edges in simulation-time units.
            coupling_values: Optional λ values used to build asymmetry surface
                over (Δτ, λ). Surface scales with channel coupling strength.

        Returns:
            Dictionary containing profiles sampled at bin centers and optional
            asymmetry surface.
        """
        if delta_tau_bins is None:
            max_delay = max(
                [float(tx['delay']) for tx in self.forward_transmission_history] +
                [float(tx['delay']) for tx in self.backward_transmission_history] +
                [max(self.forward_delay, self.backward_delay) * 0.1, 1e-3]
            )
            delta_tau_bins = np.linspace(0.0, max_delay + 1e-9, 12)
        else:
            delta_tau_bins = np.asarray(delta_tau_bins, dtype=float)

        c_a_to_b = self._aggregate_directional_communication(
            list(self.forward_transmission_history),
            delta_tau_bins,
        )
        c_b_to_a = self._aggregate_directional_communication(
            list(self.backward_transmission_history),
            delta_tau_bins,
        )

        asymmetry = c_a_to_b - c_b_to_a
        delta_tau_centers = 0.5 * (delta_tau_bins[:-1] + delta_tau_bins[1:])

        metrics = {
            'delta_tau_centers': delta_tau_centers,
            'C_A_to_B': c_a_to_b,
            'C_B_to_A': c_b_to_a,
            'asymmetry': asymmetry,
        }

        if coupling_values is not None:
            lambdas = np.asarray(coupling_values, dtype=float)
            base = max(float(self.coupling_strength), 1e-9)
            scale = (lambdas / base)[:, None]
            metrics['lambda_values'] = lambdas
            metrics['asymmetry_surface'] = scale * asymmetry[None, :]

        return metrics

    def get_statistics(self) -> Dict[str, float]:
        """
        Get comprehensive channel statistics.
        
        Returns:
            Dictionary with statistics
        """
        frame_metrics = self.compute_temporal_frame_metrics()
        asymmetry_l1 = float(np.sum(np.abs(frame_metrics['asymmetry'])))
        return {
            'vortex_state': self.vortex_state,
            'forward_quality': self.get_forward_channel_quality(),
            'backward_quality': self.get_backward_channel_quality(),
            'channel_capacity': self.channel_capacity_estimate,
            'mutual_information': self.compute_mutual_information(),
            'total_forward_bits': self.total_forward_bits,
            'total_backward_bits': self.total_backward_bits,
            'forward_transmissions': len(self.forward_transmission_history),
            'backward_transmissions': len(self.backward_transmission_history),
            'asymmetry_ratio': self.total_backward_bits / max(self.total_forward_bits, 1e-6),
            'temporal_asymmetry_l1': asymmetry_l1,
        }
    
    def visualize_signal_paths(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate visualization data for signal paths A→V→B and B→V→A.
        
        Returns:
            Tuple of (forward_path_points, backward_path_points)
        """
        if self.source_a_position is None or self.receiver_b_position is None:
            return np.array([]), np.array([])
        
        # Forward path: A → V → B
        forward_path = np.array([
            self.source_a_position,
            self.vortex_center,
            self.receiver_b_position
        ])
        
        # Backward path: B → V → A
        backward_path = np.array([
            self.receiver_b_position,
            self.vortex_center,
            self.source_a_position
        ])
        
        return forward_path, backward_path
