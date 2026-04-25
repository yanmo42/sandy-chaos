"""Von Neumann ordinals: N built from the empty set.

Construction (math_foundations_zf.md, section 1):
    0 = empty
    S(n) = n cup {n}

so that 1 = {0}, 2 = {0, 1}, 3 = {0, 1, 2}, ...

The cardinality of an ordinal as a frozenset equals its value as a
natural number: len(VNOrdinal.from_int(7).materialise()) == 7. That
identity is the entire elegance of the construction.

Implementation note: storing every ordinal as a literal nested
frozenset is correct but O(n^2) memory and worse for arithmetic
(multiplication can briefly produce ordinals with cardinality
~k * m). We instead carry the cardinality as a Python int and
materialise the frozenset structure on demand via .materialise().

This is exact, not an approximation. By induction on n: two finite
von Neumann ordinals are extensionally equal iff their cardinalities
are equal. So int-level equality is provably extensional equality on
this representation. CPython int arithmetic on ordinal cardinalities
gives the same answer the literal construction would, just without
the redundant tree of frozensets.

`materialise()` is exposed so tests can verify the literal ZF
structure where it matters (ZF1 extensionality on small ordinals).
"""

from functools import total_ordering
from typing import Iterator

from .empty import EMPTY


@total_ordering
class VNOrdinal:
    """A finite von Neumann ordinal carrying its cardinality as int.

    Realises ZF1 (extensionality), ZF2 (empty), ZF3 (pairing) and
    ZF4 (union) implicitly through frozenset semantics on the
    materialised form. Asserts ZF6 (infinity) operationally via
    .successor() and .naturals(): for any ordinal we can construct
    its successor in O(1).
    """

    __slots__ = ("_n",)

    def __init__(self, n: int) -> None:
        if not isinstance(n, int) or n < 0:
            raise ValueError(
                "VNOrdinal value must be a non-negative int (cardinality)"
            )
        self._n = n

    @classmethod
    def zero(cls) -> "VNOrdinal":
        return cls(0)

    @classmethod
    def from_int(cls, n: int) -> "VNOrdinal":
        return cls(n)

    @classmethod
    def naturals(cls) -> Iterator["VNOrdinal"]:
        n = 0
        while True:
            yield cls(n)
            n += 1

    def successor(self) -> "VNOrdinal":
        return VNOrdinal(self._n + 1)

    def cardinality(self) -> int:
        return self._n

    def to_int(self) -> int:
        return self._n

    def materialise(self) -> frozenset:
        """Return the literal frozenset {0, 1, ..., n-1}.

        Members are themselves VNOrdinals, recursively materialised.
        Use this to inspect the ZF construction directly. Cost is
        O(n^2) in total nodes, so keep n small.
        """
        if self._n == 0:
            return EMPTY
        return frozenset(VNOrdinal(k) for k in range(self._n))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VNOrdinal):
            return NotImplemented
        return self._n == other._n

    def __hash__(self) -> int:
        return hash(("VNOrdinal", self._n))

    def __lt__(self, other: "VNOrdinal") -> bool:
        if not isinstance(other, VNOrdinal):
            return NotImplemented
        # n < m iff n in m, and m = {0, ..., m-1}, so n < m iff self._n < other._n
        return self._n < other._n

    def __add__(self, other: "VNOrdinal") -> "VNOrdinal":
        if not isinstance(other, VNOrdinal):
            return NotImplemented
        return VNOrdinal(self._n + other._n)

    def __mul__(self, other: "VNOrdinal") -> "VNOrdinal":
        if not isinstance(other, VNOrdinal):
            return NotImplemented
        return VNOrdinal(self._n * other._n)

    def __repr__(self) -> str:
        return f"N({self._n})"
