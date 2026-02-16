"""
Nested Time Module
==================
Maps between external simulation time (t) and agent-local emergent time (tau),
plus meta-time (sigma) for reflective updates.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
import numpy as np


@dataclass
class NestedTimeState:
    external_time: float = 0.0
    emergent_time: complex = 0.0 + 0.0j
    meta_time: int = 0


@dataclass
class NestedTimeTracker:
    """Tracks nested time for a single agent."""

    name: str
    state: NestedTimeState = field(default_factory=NestedTimeState)
    history: list = field(default_factory=list)

    def update(self, external_time: float, complex_state: complex, ds: float = 1.0):
        """Advance emergent time using a simple path integral step."""
        self.state.external_time = external_time
        self.state.emergent_time += complex_state * ds
        self.state.meta_time += 1
        self.history.append({
            "t": external_time,
            "tau": self.state.emergent_time,
            "sigma": self.state.meta_time,
        })

    def frame_offset(self, other: "NestedTimeTracker") -> complex:
        return other.state.emergent_time - self.state.emergent_time

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "t": self.state.external_time,
            "tau": self.state.emergent_time,
            "tau_real": self.state.emergent_time.real,
            "tau_imag": self.state.emergent_time.imag,
            "sigma": self.state.meta_time,
        }