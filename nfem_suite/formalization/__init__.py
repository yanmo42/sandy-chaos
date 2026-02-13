"""
Formalization Module
====================
Provides pluggable mathematical formalizations for the duality space.
Allows swapping between different theoretical frameworks (Euler-based complex analysis,
transfinite set theory, etc.) to model order-disorder bijections and emergent time.
"""

from .base import Formalization
from .registry import FormalizationRegistry
from .complex_euler import EulerFormalization

# Global registry instance
registry = FormalizationRegistry()

# Register available formalizations
registry.register("euler", EulerFormalization)

# Set default
registry.set_active("euler")

__all__ = [
    'Formalization',
    'FormalizationRegistry', 
    'EulerFormalization',
    'registry'
]
