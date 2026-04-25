"""Q as the field of fractions of Z.

Construction (math_foundations_zf.md, section 3):
    Q = (Z x (Z \\ {0})) / ~,  where (p, q) ~ (r, s) iff p * s = q * r.

The pair (p, q) represents the rational p / q. We canonicalise by
forcing the denominator positive and dividing by the gcd of the
absolute values, so Python `==` again matches the equivalence.

Q is the smallest field containing Z. Field operations (+, -, *, /)
are defined on the pairs and lift through the equivalence.

Q is dense but incomplete: section 4 of math_foundations_zf shows
sqrt(2) is not in Q. That gap is what motivates the bridge to R in
`bridge.py`.
"""

from math import gcd

from .integer import ZInt


class QRat:
    """A rational p / q with q > 0 and gcd(|p|, q) = 1."""

    __slots__ = ("_num", "_den")

    def __init__(self, num: ZInt, den: ZInt) -> None:
        if not isinstance(num, ZInt) or not isinstance(den, ZInt):
            raise TypeError("QRat takes two ZInts")
        if den.is_zero():
            raise ZeroDivisionError("Denominator must be non-zero in Q")
        n_int = num.to_int()
        d_int = den.to_int()
        if d_int < 0:
            n_int, d_int = -n_int, -d_int
        g = gcd(abs(n_int), d_int)
        if g > 1:
            n_int //= g
            d_int //= g
        self._num = ZInt.from_int(n_int)
        self._den = ZInt.from_int(d_int)

    @classmethod
    def from_ints(cls, num: int, den: int = 1) -> "QRat":
        return cls(ZInt.from_int(num), ZInt.from_int(den))

    @classmethod
    def zero(cls) -> "QRat":
        return cls.from_ints(0, 1)

    @classmethod
    def one(cls) -> "QRat":
        return cls.from_ints(1, 1)

    def numerator(self) -> ZInt:
        return self._num

    def denominator(self) -> ZInt:
        return self._den

    def is_zero(self) -> bool:
        return self._num.is_zero()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QRat):
            return NotImplemented
        return self._num == other._num and self._den == other._den

    def __hash__(self) -> int:
        return hash((self._num, self._den))

    def __lt__(self, other: "QRat") -> bool:
        if not isinstance(other, QRat):
            return NotImplemented
        # p/q < r/s iff p*s < r*q, valid because q, s > 0
        return (self._num * other._den).to_int() < (other._num * self._den).to_int()

    def __le__(self, other: "QRat") -> bool:
        if not isinstance(other, QRat):
            return NotImplemented
        return (self._num * other._den).to_int() <= (other._num * self._den).to_int()

    def __neg__(self) -> "QRat":
        return QRat(-self._num, self._den)

    def __add__(self, other: "QRat") -> "QRat":
        if not isinstance(other, QRat):
            return NotImplemented
        # p/q + r/s = (p*s + r*q) / (q*s)
        return QRat(self._num * other._den + other._num * self._den,
                    self._den * other._den)

    def __sub__(self, other: "QRat") -> "QRat":
        if not isinstance(other, QRat):
            return NotImplemented
        return self + (-other)

    def __mul__(self, other: "QRat") -> "QRat":
        if not isinstance(other, QRat):
            return NotImplemented
        return QRat(self._num * other._num, self._den * other._den)

    def __truediv__(self, other: "QRat") -> "QRat":
        if not isinstance(other, QRat):
            return NotImplemented
        if other.is_zero():
            raise ZeroDivisionError("Division by zero in Q")
        return QRat(self._num * other._den, self._den * other._num)

    def __repr__(self) -> str:
        if self._den == ZInt.one():
            return f"Q({self._num.to_int()})"
        return f"Q({self._num.to_int()}/{self._den.to_int()})"
