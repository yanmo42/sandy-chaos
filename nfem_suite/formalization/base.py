"""
Base Abstract Class for Formalization Plugins
==============================================
Defines the interface that all mathematical formalization implementations must satisfy.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Any, Dict, List, Tuple


class Formalization(ABC):
    """
    Abstract base class for mathematical formalizations of the duality space.
    
    Each formalization provides a different theoretical framework for:
    1. Computing order/disorder parameters from system state
    2. Defining the bijection between order and disorder states
    3. Constructing complex entropy states
    4. Computing path integrals for emergent time
    5. Calculating temporal displacement in closed loops
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the formalization with optional configuration.
        
        Args:
            config: Dictionary of configuration parameters specific to this formalization
        """
        self.config = config or {}
    
    @abstractmethod
    def compute_order_parameter(self, state: Dict[str, Any]) -> float:
        """
        Compute the order parameter Ω for a given system state.
        
        Args:
            state: Dictionary containing system state information
                   (e.g., velocities, positions, mesh structure)
        
        Returns:
            Order parameter value (typically in [0, 1])
        """
        pass
    
    @abstractmethod
    def compute_disorder_parameter(self, state: Dict[str, Any]) -> float:
        """
        Compute the disorder parameter Ω̄ for a given system state.
        
        Args:
            state: Dictionary containing system state information
        
        Returns:
            Disorder parameter value (typically in [0, 1])
        """
        pass
    
    @abstractmethod
    def bijection(self, alpha: float) -> float:
        """
        Define the bijection f: Ω → Ω̄ mapping order to disorder.
        
        Args:
            alpha: Order parameter value
        
        Returns:
            Corresponding disorder parameter value beta
        """
        pass
    
    @abstractmethod
    def complex_entropy_state(self, alpha: float, beta: float) -> complex:
        """
        Construct the complex entropy state Z from order and disorder parameters.
        
        Args:
            alpha: Order parameter
            beta: Disorder parameter
        
        Returns:
            Complex number representing the entropy state
        """
        pass
    
    @abstractmethod
    def path_integral(self, path: List[np.ndarray], states: List[complex]) -> complex:
        """
        Compute the path-dependent integral for emergent time τ.
        
        Args:
            path: List of position vectors along the path
            states: List of complex entropy states at each point
        
        Returns:
            Complex-valued emergent time τ
        """
        pass
    
    @abstractmethod
    def temporal_displacement(self, loop_path: List[np.ndarray], 
                            loop_states: List[complex]) -> complex:
        """
        Compute the temporal displacement ΔT for a closed loop.
        
        Args:
            loop_path: List of positions forming a closed loop
            loop_states: List of complex entropy states around the loop
        
        Returns:
            Complex temporal displacement ΔT
        """
        pass
    
    @abstractmethod
    def get_phase(self, z: complex) -> float:
        """
        Extract the phase angle φ from a complex entropy state.
        
        Args:
            z: Complex entropy state
        
        Returns:
            Phase angle in radians
        """
        pass
    
    @abstractmethod
    def get_magnitude(self, z: complex) -> float:
        """
        Extract the magnitude |S| from a complex entropy state.
        
        Args:
            z: Complex entropy state
        
        Returns:
            Magnitude
        """
        pass
    
    def get_name(self) -> str:
        """
        Return the name of this formalization.
        
        Returns:
            String identifier for this formalization
        """
        return self.__class__.__name__
