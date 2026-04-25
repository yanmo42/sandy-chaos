"""Property tests for the ZF -> Q chain.

Each test cites the axiom or construction it exercises so the link
between the Python implementation and `docs/math_foundations_zf.md`
stays legible.
"""

import math
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nfem_suite.formalization.set_theoretic import (
    EMPTY,
    REGISTERED,
    ZF_AXIOMS,
    BridgeAssumption,
    EmptySet,
    QRat,
    VNOrdinal,
    ZInt,
    complex_entropy_state,
    cross_to_float,
    find_assumption,
    magnitude_squared_qrat,
    magnitude_to_float,
    phase_to_float,
)


class TestAxiomRegistry(unittest.TestCase):
    def test_eight_zf_axioms_plus_choice(self):
        ids = [a.id for a in ZF_AXIOMS]
        self.assertEqual(
            ids,
            ["ZF1", "ZF2", "ZF3", "ZF4", "ZF5", "ZF6", "ZF7", "ZF8", "ZFC"],
        )

    def test_each_axiom_has_realisation_text(self):
        for a in ZF_AXIOMS:
            self.assertTrue(a.realisation, f"{a.id} missing realisation")
            self.assertTrue(a.statement, f"{a.id} missing statement")
            self.assertTrue(a.formal, f"{a.id} missing formal sentence")


class TestEmptySet(unittest.TestCase):
    def test_zf2_witness_has_cardinality_zero(self):
        self.assertEqual(len(EMPTY), 0)

    def test_empty_equals_plain_frozenset(self):
        self.assertEqual(EMPTY, frozenset())

    def test_distinct_emptyset_instances_are_equal(self):
        self.assertEqual(EmptySet(), EmptySet())


class TestVonNeumannOrdinals(unittest.TestCase):
    def test_zf2_zero_materialises_to_empty(self):
        self.assertEqual(VNOrdinal.zero().materialise(), EMPTY)

    def test_one_plus_one_equals_two_via_successor(self):
        zero = VNOrdinal.zero()
        one = zero.successor()
        two = one.successor()
        self.assertEqual(one + one, two)

    def test_two_is_literally_set_of_zero_and_one(self):
        zero = VNOrdinal.zero()
        one = zero.successor()
        two = one.successor()
        self.assertEqual(two.materialise(), frozenset({zero, one}))

    def test_cardinality_equals_value_for_first_twenty(self):
        for k in range(20):
            self.assertEqual(VNOrdinal(k).cardinality(), k)
            self.assertEqual(len(VNOrdinal(k).materialise()), k)

    def test_zf1_extensionality_via_frozenset_equality(self):
        a = VNOrdinal.from_int(5)
        b = VNOrdinal.from_int(5)
        self.assertEqual(a, b)
        self.assertEqual(a.materialise(), b.materialise())

    def test_membership_orders_finite_ordinals(self):
        one = VNOrdinal.from_int(1)
        two = VNOrdinal.from_int(2)
        self.assertIn(one, two.materialise())
        self.assertLess(one, two)

    def test_addition_commutative_small_range(self):
        for a in range(8):
            for b in range(8):
                self.assertEqual(VNOrdinal(a) + VNOrdinal(b),
                                 VNOrdinal(b) + VNOrdinal(a))

    def test_multiplication_distributes_over_addition(self):
        for a in range(5):
            for b in range(5):
                for c in range(5):
                    lhs = VNOrdinal(a) * (VNOrdinal(b) + VNOrdinal(c))
                    rhs = VNOrdinal(a) * VNOrdinal(b) + VNOrdinal(a) * VNOrdinal(c)
                    self.assertEqual(lhs, rhs)

    def test_naturals_iterator_produces_consecutive_ordinals(self):
        gen = VNOrdinal.naturals()
        for k in range(10):
            self.assertEqual(next(gen), VNOrdinal(k))


class TestIntegers(unittest.TestCase):
    def test_subtraction_closed_in_z_not_n(self):
        one = ZInt.from_int(1)
        two = ZInt.from_int(2)
        self.assertEqual((one - two).to_int(), -1)

    def test_additive_inverse(self):
        for k in range(-10, 11):
            a = ZInt.from_int(k)
            self.assertTrue((a + (-a)).is_zero())

    def test_negative_times_negative_is_positive(self):
        self.assertEqual(
            ZInt.from_int(-7) * ZInt.from_int(-3),
            ZInt.from_int(21),
        )

    def test_canonical_form_is_unique(self):
        from nfem_suite.formalization.set_theoretic.ordinal import VNOrdinal as O
        a = ZInt(O.from_int(3), O.from_int(5))
        b = ZInt(O.from_int(0), O.from_int(2))
        c = ZInt(O.from_int(7), O.from_int(9))
        self.assertEqual(a, b)
        self.assertEqual(b, c)
        self.assertEqual(a, ZInt.from_int(-2))


class TestRationals(unittest.TestCase):
    def test_canonicalisation_to_lowest_terms(self):
        self.assertEqual(QRat.from_ints(2, 4), QRat.from_ints(1, 2))
        self.assertEqual(QRat.from_ints(-2, 4), QRat.from_ints(-1, 2))
        self.assertEqual(QRat.from_ints(0, 7), QRat.from_ints(0, 1))

    def test_addition_of_thirds(self):
        third = QRat.from_ints(1, 3)
        self.assertEqual(third + third + third, QRat.one())

    def test_multiplicative_inverse(self):
        for n in range(1, 8):
            for d in range(1, 8):
                q = QRat.from_ints(n, d)
                self.assertEqual(q * (QRat.one() / q), QRat.one())

    def test_distributivity_over_addition(self):
        a = QRat.from_ints(2, 3)
        b = QRat.from_ints(5, 7)
        c = QRat.from_ints(-1, 4)
        self.assertEqual(a * (b + c), a * b + a * c)

    def test_division_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            QRat.one() / QRat.zero()

    def test_sqrt_two_not_in_q_bounded_search(self):
        target = QRat.from_ints(2, 1)
        for n in range(0, 100):
            for d in range(1, 100):
                q = QRat.from_ints(n, d)
                self.assertNotEqual(q * q, target)


class TestBridgeAssumptions(unittest.TestCase):
    def test_pinned_assumption_ids(self):
        ids = {a.id for a in REGISTERED}
        self.assertEqual(ids, {"B-001", "B-002", "B-003"})

    def test_assumption_lookup(self):
        a = find_assumption("B-001")
        self.assertIsNotNone(a)
        assert isinstance(a, BridgeAssumption)
        self.assertIn("IEEE-754", a.name)

    def test_each_assumption_has_failure_mode(self):
        for a in REGISTERED:
            self.assertTrue(a.failure_mode, f"{a.id} missing failure_mode")
            self.assertTrue(a.used_for, f"{a.id} missing used_for")


class TestBridgeCrossings(unittest.TestCase):
    def test_cross_to_float_on_simple_rational(self):
        self.assertEqual(cross_to_float(QRat.from_ints(1, 2)), 0.5)
        self.assertEqual(cross_to_float(QRat.from_ints(-3, 4)), -0.75)

    def test_pythagorean_3_4_5_stays_exact_in_q(self):
        # alpha = 3/5, beta = 4/5  =>  |Z|^2 = 9/25 + 16/25 = 1 exactly
        alpha = QRat.from_ints(3, 5)
        beta = QRat.from_ints(4, 5)
        self.assertEqual(magnitude_squared_qrat(alpha, beta), QRat.one())

    def test_magnitude_crossing_returns_unit_for_3_4_5(self):
        alpha = QRat.from_ints(3, 5)
        beta = QRat.from_ints(4, 5)
        self.assertAlmostEqual(magnitude_to_float(alpha, beta), 1.0, places=15)

    def test_phase_crossing_matches_atan2_within_one_ulp(self):
        alpha = QRat.from_ints(3, 5)
        beta = QRat.from_ints(4, 5)
        # B-001 means we may differ by one ULP from the reference path.
        self.assertAlmostEqual(
            phase_to_float(alpha, beta),
            math.atan2(4, 3),
            places=14,
        )

    def test_complex_entropy_state_construction(self):
        alpha = QRat.from_ints(1, 2)
        beta = QRat.from_ints(1, 2)
        z = complex_entropy_state(alpha, beta)
        self.assertEqual(z, complex(0.5, 0.5))


if __name__ == "__main__":
    unittest.main()
