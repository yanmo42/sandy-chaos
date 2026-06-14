# Contract 8 Receipt — Verifier-Lane Hardening (AUD-008 / AUD-009)

Date: 2026-06-14
Commit: c2f16ea
Branch: main
Status: COMPLETE

## Kill Criterion

Synthetic PASS payload without comparator_class is rejected by the validator. VERIFIED — test_pass_transition_hardening.py::test_pass_without_comparator_class_is_rejected passes.

## Changes

scripts/validate_foundations.py
  - Added PASS_REQUIRED_FIELDS tuple: comparator_class, strongest_mundane_comparator, independent_rederivation
  - Added _check_pass_transition_fields() — returns error strings for each missing or empty field
  - Wired into validate_evidence_payload(): when declared_decision == "PASS", errors are extended with any missing field errors

spine/concepts/SC-CONCEPT-0011-strongest-mundane-comparator.yaml (new)
  - id: SC-CONCEPT-0011 (SC-CONCEPT-0010 was already taken by closed-loop-causal-leverage)
  - name: Strongest-Mundane-Comparator Requirement
  - claim_tier: defensible
  - lane: theory
  - failure_conditions: strawman baseline can be reproduced by a simpler mundane model not tested; each of the three PASS fields absent or empty
  - cross-links: AUD-009, A-003, A-004 (in notes)
  - implemented_in: scripts/validate_foundations.py
  - tested_by: tests/test_pass_transition_hardening.py

tests/test_pass_transition_hardening.py (new, 6 cases)
  - test_pass_without_comparator_class_is_rejected — PASS
  - test_pass_without_strongest_mundane_comparator_is_rejected — PASS
  - test_pass_without_independent_rederivation_is_rejected — PASS
  - test_pass_with_empty_comparator_class_is_rejected — PASS
  - test_pass_with_all_three_fields_is_accepted — PASS
  - test_non_pass_decision_does_not_require_comparator_fields — PASS

nfem_suite/intelligence/leverage/scorer.py
  - evidence_payload() now extracts baseline.comparator_class, baseline.strongest_mundane_comparator, and verification.independent_rederivation from card data and emits them into the foundations-compatible payload

tests/test_causality_invariants.py
  - _valid_payload() updated to include all three PASS-required fields

tests/test_leverage_card.py
  - _minimal_payload() updated: baseline block now has comparator_class and strongest_mundane_comparator; verification block has independent_rederivation

## Test Result

344 passed, 6 subtests passed (excluding scipy/matplotlib-dependent tests test_core.py and test_dashboard_traces.py which fail due to missing system packages unrelated to this contract)

## Audit Notes

The original AUD-008/AUD-009 finding was that validate_foundations.py only caught violations when the payload self-declared them (honor system). The recurring failure mode was weak/strawman comparator classes: sign-mismatched boost instead of Sagnac (T-015); channel-off instead of history-forecaster (subcritical). The new check is structural — any PASS-claiming payload that omits or empties any of the three required fields is downgraded to REVIEW and the specific missing field is named in the error.
