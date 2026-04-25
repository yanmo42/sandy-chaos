"""Constructive realization of the ZF -> Q chain.

This package implements the first four arrows of the derivation chain
documented in `docs/math_foundations_zf.md`:

    empty -> N -> Z -> Q

Everything in this layer is exact: no floating-point approximation, no
numerical truncation. Set-theoretic equivalences are realised by
canonical-form representatives, so Python's `==` matches the underlying
mathematical equivalence.

The crossing from Q to R is the responsibility of `bridge.py`, which
enumerates each named approximation assumption (B-001, B-002, ...) so
the project can audit where exactness ends.
"""

from .axioms import ZF_AXIOMS, ZFAxiom
from .empty import EMPTY, EmptySet
from .ordinal import VNOrdinal
from .integer import ZInt
from .rational import QRat
from .bridge import (
    REGISTERED,
    BridgeAssumption,
    complex_entropy_state,
    cross_to_float,
    find_assumption,
    list_assumptions,
    magnitude_squared_qrat,
    magnitude_to_float,
    phase_to_float,
)

__all__ = [
    "ZF_AXIOMS",
    "ZFAxiom",
    "EMPTY",
    "EmptySet",
    "VNOrdinal",
    "ZInt",
    "QRat",
    "REGISTERED",
    "BridgeAssumption",
    "list_assumptions",
    "find_assumption",
    "cross_to_float",
    "magnitude_squared_qrat",
    "magnitude_to_float",
    "phase_to_float",
    "complex_entropy_state",
]
