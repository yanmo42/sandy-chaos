# Symbolic Maps Operator Canonicalization Probe v0

**Date:** 2026-04-16  
**Owner surface:** sandy-chaos  
**Status:** active frontier bounded follow-on  
**Targets:** `SC-CONCEPT-0006`  
**Depends on:** `plans/symbolic_maps_operator_vocabulary_pressure_result_v0.md`

---

## Purpose

Run the final tiny probe requested by the operator-vocabulary pressure pass:

> can the current four-artifact operator labels be mapped into the smallest plausible canonical operator vocabulary for the active query families without heavy hand-translation?

This is still bounded.
It does not broaden the corpus, change the schema, or reopen adjacent concepts.

---

## Benchmark target

Construct the smallest canonical operator vocabulary that could plausibly support the current three query families:

- `structural_normalization`
- `constraint_discipline`
- `comparison_reuse`

Then test whether current operator labels map cleanly into that vocabulary.

The pressure question is:

> does the vocabulary look discovered from the artifacts, or imposed onto them?

---

## Pre-evaluation success, failure, and ambiguity conditions

### Success condition
Treat the probe as sufficient to preserve hardening candidacy only if **all** are true:

1. At least **70%** of current operator labels map to the canonical vocabulary by direct lexical fit or trivial inflectional variation.
2. No more than **20%** of labels require semantic hand-translation.
3. All three query families retain at least one multi-artifact canonical operator after mapping.

### Failure condition
Treat the probe as a demotion signal for hardening candidacy if **any** are true:

1. More than **25%** of labels require semantic hand-translation.
2. One or more query families survive only because the canonical vocabulary was imposed broadly rather than lexically earned.
3. The mapped vocabulary compresses labels cosmetically but still does not produce shared multi-artifact operators.

### Ambiguity condition
Treat the probe as ambiguous if:

1. mapping coverage is high,
2. but shared multi-artifact operators remain thin,
3. and the result still depends on a few arguable semantic merges.

---

## Canonical vocabulary rule

Keep the vocabulary as small as possible.
Do not allow it to grow just to rescue coverage.

If a mapping needs a conceptual paraphrase rather than a near-lexical fit, count it as semantic hand-translation.

---

## Deliverables

1. This benchmark note.
2. `scripts/symbolic_maps_operator_canonicalization_probe_v0.py`
3. `memory/research/symbolic-maps-level4/operator_canonicalization_probe_v0.json`
4. `memory/research/symbolic-maps-level4/operator_canonicalization_probe_v0_summary.md`
5. one result note with the final advance / hold / demote-hardening-candidacy decision.

---

## Immediate next action

Run the canonicalization probe now and decide whether schema-hardening candidacy for `SC-CONCEPT-0006` should stay active or be demoted.
