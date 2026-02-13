"""
Formalization Registry
======================
Manages available formalizations and allows runtime swapping between them.
"""

from typing import Dict, Type, Optional
from .base import Formalization


class FormalizationRegistry:
    """
    Registry for managing mathematical formalization implementations.
    Allows registering new formalizations and switching between them at runtime.
    """
    
    def __init__(self):
        self._formalizations: Dict[str, Type[Formalization]] = {}
        self._active_name: Optional[str] = None
        self._active_instance: Optional[Formalization] = None
    
    def register(self, name: str, formalization_class: Type[Formalization]):
        """
        Register a new formalization implementation.
        
        Args:
            name: Identifier for this formalization (e.g., "euler", "transfinite")
            formalization_class: Class implementing the Formalization interface
        """
        if not issubclass(formalization_class, Formalization):
            raise TypeError(f"{formalization_class} must be a subclass of Formalization")
        
        self._formalizations[name] = formalization_class
        print(f"Registered formalization: {name}")
    
    def set_active(self, name: str, config: dict = None):
        """
        Set the active formalization.
        
        Args:
            name: Name of the formalization to activate
            config: Optional configuration dictionary for the formalization
        
        Raises:
            KeyError: If the formalization name is not registered
        """
        if name not in self._formalizations:
            available = ', '.join(self._formalizations.keys())
            raise KeyError(
                f"Formalization '{name}' not found. Available: {available}"
            )
        
        self._active_name = name
        self._active_instance = self._formalizations[name](config)
        print(f"Active formalization set to: {name}")
    
    def get_active(self) -> Formalization:
        """
        Get the currently active formalization instance.
        
        Returns:
            The active Formalization instance
        
        Raises:
            RuntimeError: If no formalization has been set active
        """
        if self._active_instance is None:
            raise RuntimeError(
                "No active formalization. Call set_active() first."
            )
        return self._active_instance
    
    def get_active_name(self) -> str:
        """
        Get the name of the currently active formalization.
        
        Returns:
            Name of the active formalization
        """
        return self._active_name
    
    def list_available(self) -> list:
        """
        List all registered formalization names.
        
        Returns:
            List of registered formalization names
        """
        return list(self._formalizations.keys())
    
    def is_registered(self, name: str) -> bool:
        """
        Check if a formalization is registered.
        
        Args:
            name: Formalization name to check
        
        Returns:
            True if registered, False otherwise
        """
        return name in self._formalizations
