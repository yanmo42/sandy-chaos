"""Z as equivalence classes of pairs of natural numbers.

Construction (math_foundations_zf.md, section 2):
    Z = (N x N) / ~,  where (a, b) ~ (c, d) iff a + d = b + c.

The pair (a, b) represents the integer a - b. Two pairs are
equivalent iff they describe the same difference.

We store each integer in canonical form so that Python `==` matches
the equivalence: exactly one of (a, b) is zero. Sign is recovered by
which side is non-zero.

Group completion lifts addition from N to Z and supplies additive
inverses; that is the whole point of the construction. The Theorems
in section 2 (commutativity, identity, inverses) are therefore facts
about this representation, derivable by computation.
"""

from .ordinal import VNOrdinal


class ZInt:
    """An integer as a canonical pair (positive_part, negative_part).

    Exactly one component is `VNOrdinal.zero()`. The other holds the
    absolute value as an ordinal.
    """

    __slots__ = ("_pos", "_neg")

    def __init__(self, a: VNOrdinal, b: VNOrdinal) -> None:
        if not isinstance(a, VNOrdinal) or not isinstance(b, VNOrdinal):
            raise TypeError("ZInt takes two VNOrdinals")
        ka, kb = a.cardinality(), b.cardinality()
        if ka >= kb:
            self._pos = VNOrdinal.from_int(ka - kb)
            self._neg = VNOrdinal.zero()
        else:
            self._pos = VNOrdinal.zero()
            self._neg = VNOrdinal.from_int(kb - ka)

    @classmethod
    def from_int(cls, n: int) -> "ZInt":
        if n >= 0:
            return cls(VNOrdinal.from_int(n), VNOrdinal.zero())
        return cls(VNOrdinal.zero(), VNOrdinal.from_int(-n))

    @classmethod
    def zero(cls) -> "ZInt":
        return cls.from_int(0)

    @classmethod
    def one(cls) -> "ZInt":
        return cls.from_int(1)

    def positive_part(self) -> VNOrdinal:
        return self._pos

    def negative_part(self) -> VNOrdinal:
        return self._neg

    def to_int(self) -> int:
        return self._pos.cardinality() - self._neg.cardinality()

    def is_zero(self) -> bool:
        return self._pos.cardinality() == 0 and self._neg.cardinality() == 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ZInt):
            return NotImplemented
        return self._pos == other._pos and self._neg == other._neg

    def __hash__(self) -> int:
        return hash((self._pos, self._neg))

    def __lt__(self, other: "ZInt") -> bool:
        if not isinstance(other, ZInt):
            return NotImplemented
        return self.to_int() < other.to_int()

    def __le__(self, other: "ZInt") -> bool:
        if not isinstance(other, ZInt):
            return NotImplemented
        return self.to_int() <= other.to_int()

    def __neg__(self) -> "ZInt":
        return ZInt(self._neg, self._pos)

    def __add__(self, other: "ZInt") -> "ZInt":
        if not isinstance(other, ZInt):
            return NotImplemented
        return ZInt(self._pos + other._pos, self._neg + other._neg)

    def __sub__(self, other: "ZInt") -> "ZInt":
        if not isinstance(other, ZInt):
            return NotImplemented
        return self + (-other)

    def __mul__(self, other: "ZInt") -> "ZInt":
        if not isinstance(other, ZInt):
            return NotImplemented
        # (a - b)(c - d) = (ac + bd) - (ad + bc)
        a, b = self._pos, self._neg
        c, d = other._pos, other._neg
        return ZInt(a * c + b * d, a * d + b * c)

    def __repr__(self) -> str:
        return f"Z({self.to_int()})"
