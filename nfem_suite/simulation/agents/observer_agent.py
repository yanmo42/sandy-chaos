"""
Observer Agent Module
=====================
Defines a minimal observer agent with memory matrix, concentration
parameters, and integration with the IdeaField.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np

from nfem_suite.intelligence.cognition.idea_field import IdeaField


@dataclass
class ConcentrationParameters:
    """Compact agent parameters controlling idea collapse dynamics."""

    collapse_intensity: float = 1.0
    attractor_depth: float = 1.0
    novelty_temperature: float = 1.0
    write_gain: float = 1.0
    read_gain: float = 1.0

    def informational_gravity(self, epsilon: float = 1e-6) -> float:
        return float(self.attractor_depth / max(self.novelty_temperature, epsilon))


@dataclass
class ObserverAgent:
    """Represents an observer with a cognitive idea field and memory."""

    name: str
    idea_basis: list
    params: ConcentrationParameters = field(default_factory=ConcentrationParameters)
    rng_seed: Optional[int] = None
    memory_matrix: np.ndarray = field(init=False)
    idea_field: IdeaField = field(init=False)
    last_collapse: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.idea_field = IdeaField(self.idea_basis, rng_seed=self.rng_seed)
        size = len(self.idea_basis)
        self.memory_matrix = np.eye(size, dtype=float)

    def update_logits(self, attention: Optional[np.ndarray] = None,
                      channel_bias: Optional[np.ndarray] = None,
                      novelty_noise: Optional[np.ndarray] = None):
        """Compute logits combining attention, memory, channel, and novelty."""
        size = len(self.idea_basis)
        attention = np.zeros(size) if attention is None else attention
        channel_bias = np.zeros(size) if channel_bias is None else channel_bias
        novelty_noise = np.zeros(size) if novelty_noise is None else novelty_noise

        memory_influence = self.memory_matrix @ self.idea_field.distribution
        logits = (
            self.params.collapse_intensity * attention
            + self.params.attractor_depth * memory_influence
            + self.params.write_gain * channel_bias
            + self.params.novelty_temperature * novelty_noise
        )
        self.idea_field.update_distribution(logits)

    def collapse(self) -> Dict[str, Any]:
        """Collapse current idea distribution to a realized idea and update memory."""
        event = self.idea_field.sample_collapse()
        idx = event["index"]

        # Simple memory reinforcement on the chosen index.
        reinforce = np.zeros_like(self.memory_matrix)
        reinforce[idx, idx] = 1.0
        self.memory_matrix = 0.95 * self.memory_matrix + 0.05 * reinforce
        self.last_collapse = event
        return event

    def diagnostics(self) -> Dict[str, Any]:
        """Return key metrics for dashboards/logging."""
        od = self.idea_field.order_disorder()
        return {
            "name": self.name,
            "order": od["order"],
            "disorder": od["disorder"],
            "entropy": self.idea_field.entropy(),
            "novelty": self.idea_field.novelty_index(),
            "informational_gravity": self.params.informational_gravity(),
        }