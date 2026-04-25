"""The Zermelo-Fraenkel axioms as a machine-readable contract.

Each axiom is recorded as a `ZFAxiom` with:
  - `id` (e.g. "ZF1")
  - `name`
  - `statement` (informal, plain text)
  - `formal` (the first-order sentence, as text)
  - `realisation` (how this layer encodes it, or why we skip it)

These records are the *contract* between `docs/math_foundations_zf.md`
and the Python representations under this package. Tests in
`tests/test_set_theoretic_chain.py` cite these IDs to make it clear
which axiom each property check is exercising.

We are not proving the axioms here. CPython is the metatheory; ZF is
expressed by choosing representations that make each axiom either
structurally true (ZF1 via frozenset equality) or constructively
realisable (ZF6 via a successor iterator).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ZFAxiom:
    id: str
    name: str
    statement: str
    formal: str
    realisation: str


ZF_AXIOMS: tuple[ZFAxiom, ...] = (
    ZFAxiom(
        id="ZF1",
        name="Extensionality",
        statement="Two sets are equal iff they have the same members.",
        formal="forall A forall B [forall x (x in A <-> x in B) -> A = B]",
        realisation=(
            "Structural: every set in this layer is a frozenset (or a "
            "canonical-form wrapper around frozensets), so Python `==` "
            "is literally extensional equality."
        ),
    ),
    ZFAxiom(
        id="ZF2",
        name="Empty Set",
        statement="There exists a set with no elements.",
        formal="exists E forall x (x not in E)",
        realisation=(
            "EMPTY = EmptySet() in empty.py. Witness is a frozenset of "
            "size zero."
        ),
    ),
    ZFAxiom(
        id="ZF3",
        name="Pairing",
        statement="For any a, b there exists the set {a, b}.",
        formal="forall a forall b exists P forall x [x in P <-> (x = a or x = b)]",
        realisation=(
            "Implicit: frozenset({a, b}) realises pairing whenever a and "
            "b are hashable. Used inside successor() in ordinal.py."
        ),
    ),
    ZFAxiom(
        id="ZF4",
        name="Union",
        statement="For any family F there exists the union of all its members.",
        formal="forall F exists U forall x [x in U <-> exists A in F (x in A)]",
        realisation=(
            "Implicit: frozenset.union and the `|` operator. Used by "
            "successor: S(n) = n | {n}."
        ),
    ),
    ZFAxiom(
        id="ZF5",
        name="Power Set",
        statement="For any A, the set of all subsets of A exists.",
        formal="forall A exists P forall S [S in P <-> S subset_of A]",
        realisation=(
            "Not constructed eagerly. For finite A we can enumerate "
            "subsets on demand; for infinite A we do not materialise "
            "the power set. Not load-bearing for the Q chain."
        ),
    ),
    ZFAxiom(
        id="ZF6",
        name="Infinity",
        statement="There exists an inductive set containing 0 and closed under successor.",
        formal="exists I [empty in I and forall x (x in I -> x cup {x} in I)]",
        realisation=(
            "We do not materialise omega as a Python value (it would be "
            "an infinite frozenset). Instead we expose VNOrdinal.zero() "
            "and .successor() and an iterator naturals() that produces "
            "every ordinal in finite time. ZF6 is asserted operationally: "
            "for any n we can produce S(n)."
        ),
    ),
    ZFAxiom(
        id="ZF7",
        name="Replacement (schema)",
        statement="The image of a set under a definable function is a set.",
        formal=(
            "for any phi: forall x in A exists! y phi(x, y) -> "
            "exists B forall y [y in B <-> exists x in A phi(x, y)]"
        ),
        realisation=(
            "Implicit: any Python function that is total over a finite "
            "set realises one instance of the schema. We rely on this "
            "for canonical-form computations in ZInt and QRat."
        ),
    ),
    ZFAxiom(
        id="ZF8",
        name="Foundation (Regularity)",
        statement="Every non-empty set has an element disjoint from it; no set contains itself.",
        formal="forall A [A != empty -> exists x in A (x cap A = empty)]",
        realisation=(
            "Structural: frozensets cannot contain themselves (you "
            "cannot construct one whose hash depends on its own "
            "identity). Foundation holds by Python's value semantics."
        ),
    ),
    ZFAxiom(
        id="ZFC",
        name="Choice",
        statement="For any family of non-empty sets, a selection function exists.",
        formal=(
            "forall F [empty not in F -> "
            "exists f: F -> union F  forall A in F (f(A) in A)]"
        ),
        realisation=(
            "Not used directly in this layer. The Q-chain constructions "
            "do not require Choice. Flagged here for completeness; if "
            "future layers (e.g. unbounded R constructions) need it, the "
            "selection function must be made explicit."
        ),
    ),
)
