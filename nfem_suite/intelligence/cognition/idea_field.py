"""
Idea Field Module
=================
Defines a minimal cognitive state field for agents: idea basis, probability
distribution, entropy, novelty, and collapse sampling.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class IdeaField:
    """Represents an agent's probabilistic idea landscape."""

    idea_basis: List[str]
    rng_seed: Optional[int] = None
    distribution: np.ndarray = field(init=False)
    history: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def __post_init__(self):
        if not self.idea_basis:
            raise ValueError("idea_basis must contain at least one idea.")
        self._rng = np.random.default_rng(self.rng_seed)
        self.distribution = np.ones(len(self.idea_basis), dtype=float)
        self.distribution /= np.sum(self.distribution)

    def entropy(self) -> float:
        """Normalized Shannon entropy for the idea distribution."""
        p = self.distribution[self.distribution > 0]
        raw_entropy = -np.sum(p * np.log(p))
        return float(raw_entropy / np.log(len(self.distribution)))

    def order_disorder(self) -> Dict[str, float]:
        """Return Ω and Ω̄ derived from normalized entropy."""
        disorder = self.entropy()
        order = 1.0 - disorder
        return {"order": float(order), "disorder": float(disorder)}

    def update_distribution(self, logits: np.ndarray):
        """Apply a logits vector to update the distribution via softmax."""
        if logits.shape[0] != len(self.idea_basis):
            raise ValueError("logits must match idea_basis length")
        stable = logits - np.max(logits)
        exp = np.exp(stable)
        self.distribution = exp / np.sum(exp)

    def sample_collapse(self) -> Dict[str, Any]:
        """Sample a realized idea from the distribution and log the event."""
        idx = int(self._rng.choice(len(self.idea_basis), p=self.distribution))
        idea = self.idea_basis[idx]
        event = {
            "idea": idea,
            "index": idx,
            "entropy": self.entropy(),
            "distribution": self.distribution.copy(),
        }
        self.history.append(event)
        return event

    def novelty_index(self) -> float:
        """Distance from rolling centroid of past collapses (simple novelty metric)."""
        if len(self.history) < 2:
            return 0.0
        indices = np.array([h["index"] for h in self.history], dtype=float)
        centroid = np.mean(indices)
        return float(abs(indices[-1] - centroid) / max(len(self.idea_basis) - 1, 1))