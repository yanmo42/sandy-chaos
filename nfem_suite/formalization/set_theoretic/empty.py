"""ZF2: the empty set.

The sole primitive object of the entire chain. Every other set in this
package is built from this one.
"""

from typing import Final


class EmptySet(frozenset):
    """The unique witness of ZF2.

    Subclasses frozenset so that membership and equality are inherited.
    The only frozenset of cardinality zero, and structural equality
    (ZF1) makes all instances of EmptySet equal to one another and to
    `frozenset()`.
    """

    __slots__ = ()

    def __new__(cls) -> "EmptySet":
        return super().__new__(cls)

    def __repr__(self) -> str:
        return "empty"


EMPTY: Final[EmptySet] = EmptySet()
