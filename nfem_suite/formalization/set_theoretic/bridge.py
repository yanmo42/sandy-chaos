"""The R-bridge: where exactness ends.

The chain empty -> N -> Z -> Q is exact in this package. R is not.
Cantor's diagonal argument shows R is uncountable; Python objects are
countable; therefore no Python value can represent every real number.
We cross by approximation, and this module enumerates each crossing.

The point is not to hide the approximation. It is to make the
boundary visible: every helper here is a *labelled* crossing, citing
the assumption(s) it relies on.

Pre-registered assumptions:

  B-001  IEEE-754 binary64 approximates R.
  B-002  Trapezoidal Riemann sum approximates the integral.
  B-003  numpy.angle / atan2 branch cut at phi = pi is library-defined.

If new crossings are introduced (e.g. mpmath arbitrary precision,
interval arithmetic, computable-real backends) they should be added
here as new BridgeAssumption rows.
"""

import math
from dataclasses import dataclass

from .rational import QRat


@dataclass(frozen=True)
class BridgeAssumption:
    id: str
    name: str
    used_for: str
    failure_mode: str


REGISTERED: tuple[BridgeAssumption, ...] = (
    BridgeAssumption(
        id="B-001",
        name="IEEE-754 binary64 approximates R",
        used_for=(
            "any operation that returns a Python float: sqrt, exp, sin, "
            "cos, integration kernels, complex coordinates"
        ),
        failure_mode=(
            "non-associative addition; catastrophic cancellation near "
            "subtractive boundaries; fixed 53-bit mantissa"
        ),
    ),
    BridgeAssumption(
        id="B-002",
        name="Trapezoidal Riemann sum approximates the line integral",
        used_for=(
            "path_integral, temporal_displacement, any contour integral "
            "in the Euler formalisation"
        ),
        failure_mode=(
            "O(N^-2) error for smooth integrands; degrades for "
            "non-smooth Z; cannot detect singularities lying between "
            "sample points"
        ),
    ),
    BridgeAssumption(
        id="B-003",
        name="atan2 branch cut at phi = pi is library-defined",
        used_for="phase extraction, winding number computation",
        failure_mode=(
            "boundary value at phi = pi may differ between math.atan2 "
            "and numpy.angle; portability risk for tests that pin the "
            "branch-cut behaviour"
        ),
    ),
)


def list_assumptions() -> tuple[BridgeAssumption, ...]:
    return REGISTERED


def find_assumption(aid: str) -> BridgeAssumption | None:
    for a in REGISTERED:
        if a.id == aid:
            return a
    return None


def cross_to_float(q: QRat) -> float:
    """Cross from exact Q to IEEE-754. Crosses B-001.

    The numerator and denominator are exact integers; their ratio as a
    Python float is rounded to the nearest representable double.
    """
    return q.numerator().to_int() / q.denominator().to_int()


def magnitude_squared_qrat(alpha: QRat, beta: QRat) -> QRat:
    """Return |Z|^2 = alpha^2 + beta^2 in Q. No bridge crossing.

    The squared magnitude stays exact. Only sqrt forces the crossing,
    so any test or check expressible against |Z|^2 should prefer this
    form over magnitude(...).
    """
    return alpha * alpha + beta * beta


def magnitude_to_float(alpha: QRat, beta: QRat) -> float:
    """|Z| = sqrt(alpha^2 + beta^2). Crosses B-001 (sqrt)."""
    return math.sqrt(cross_to_float(magnitude_squared_qrat(alpha, beta)))


def phase_to_float(alpha: QRat, beta: QRat) -> float:
    """phi = atan2(beta, alpha). Crosses B-001 and B-003.

    Result is in (-pi, pi]; the boundary value at phi = pi is set by
    the underlying math library.
    """
    return math.atan2(cross_to_float(beta), cross_to_float(alpha))


def complex_entropy_state(alpha: QRat, beta: QRat) -> complex:
    """Construct Z = alpha + i*beta. Crosses B-001 (twice).

    This is the labelled bridge from the set-theoretic chain into the
    complex entropy state used by EulerFormalization. The two
    coordinate crossings are explicit; downstream consumers know they
    are operating on IEEE-754 floats from this point forward.
    """
    return complex(cross_to_float(alpha), cross_to_float(beta))
