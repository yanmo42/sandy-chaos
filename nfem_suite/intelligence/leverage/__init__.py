"""Causal leverage card harness (SC-CONCEPT-0010).

A causal leverage card is the on-disk artifact that operationalises the
closed-loop "actualized intelligence = verified causal leverage per constrained
resource" framing from `docs/21_closed_loop_causal_leverage.md`. Each card
declares an objective, baseline, intervention, denominators, risk vector,
reversibility class, failure conditions, verification method, and measured
outcome before yielding a decision.

The public API is intentionally small:

    from nfem_suite.intelligence.leverage import (
        LeverageCard,
        load_card,
        score_card,
        evidence_payload,
    )

`score_card` is pure: schema validation only, no I/O. `evidence_payload` returns
a dict compatible with `scripts/validate_foundations.py` so the harness plugs
into the existing theory-implementation matrix evidence flow.
"""

from .card import LeverageCard, load_card
from .scorer import ScoreReport, evidence_payload, score_card

__all__ = [
    "LeverageCard",
    "ScoreReport",
    "evidence_payload",
    "load_card",
    "score_card",
]
