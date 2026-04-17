# Symbolic Maps Operator Vocabulary Pressure v0

**Date:** 2026-04-16  
**Owner surface:** sandy-chaos  
**Status:** active frontier bounded follow-on  
**Targets:** `SC-CONCEPT-0006`  
**Depends on:** `plans/symbolic_maps_level4_schema_hardening_gate_result_v0.md`

---

## Purpose

Run the next bounded follow-on requested by the schema-hardening gate:

> test whether the current four-artifact frontier can answer a tiny cross-artifact operator-vocabulary query set using naturally recurring reusable terms, rather than only by hand-authored synonym glue.

This pass stays narrowly scoped to `SC-CONCEPT-0006`.
It does not add new schema fields, broaden the corpus, or harden anything.

---

## Benchmark target

Use the existing four-artifact normalization sketch and ask one focused question:

> Can the current operator vocabulary support cross-artifact query discrimination with mostly direct lexical reuse, or does it only become queryable after manual alias stitching?

The pressure target is operator vocabulary only.
Not slot-family coverage.
Not broad concept evaluation.

---

## Evidence reviewed before evaluation

1. `state/ygg/active-work.json`
2. `spine/concepts/SC-CONCEPT-0006.yaml`
3. `plans/symbolic_maps_level4_scoring_pass_v1.md`
4. `plans/symbolic_maps_level4_normalization_sketch_v0.md`
5. `plans/symbolic_maps_level4_schema_hardening_gate_v0.md`
6. `plans/symbolic_maps_level4_schema_hardening_gate_result_v0.md`
7. `memory/research/symbolic-maps-level4/normalization_sketch_v0.json`
8. `memory/research/symbolic-maps-level4/schema_hardening_gate_v0.json`

---

## Query set

Use only three tiny operator-vocabulary query families:

1. **structural_normalization**
   - can the artifact vocabulary answer a query about extracting, translating, normalizing, labeling, or packetizing structure?
2. **constraint_discipline**
   - can the artifact vocabulary answer a query about binding operators to constraints, failures, boundaries, or validation discipline?
3. **comparison_reuse**
   - can the artifact vocabulary answer a query about retrieval, composition, bridging, or bundling for later comparison/reuse?

No fourth query family unless this set proves unreadable.

---

## Pre-evaluation success, failure, and ambiguity conditions

### Success condition
Treat the pass as strong enough to support movement toward hardening only if **both** are true:

1. At least **two** query families can be answered across **three or more artifacts** using mostly direct lexical support from the operator labels themselves.
2. Any alias help is minor, meaning it adds at most **one artifact** to a query family rather than creating the family almost from scratch.

### Failure condition
Treat the pass as a hold signal if **any** of these happen:

1. Only one query family reaches three-artifact support directly.
2. A second family reaches useful coverage only after hand-authored alias stitching.
3. The current operator vocabulary looks comparison-usable only because manual mapping is doing the real work.

### Ambiguity condition
Treat the pass as ambiguous if:

1. one family is clearly direct,
2. a second family is close but not clean,
3. and the difference between natural lexical reuse and alias assistance is small enough that the lane could go either way after one more tiny pass.

---

## Method

1. Load `normalization_sketch_v0.json` only.
2. Split operator labels into simple subtokens.
3. Measure query-family support in two ways:
   - **direct support** using anchor tokens already present in operator labels,
   - **alias-assisted support** using a tiny explicit synonym layer.
4. Reject hardening if the useful multi-artifact coverage appears mainly in the alias-assisted layer.

This is intentionally strict.
If the family needs a translator table to look converged, it is not ready to harden.

---

## Deliverables

1. This benchmark note.
2. `scripts/symbolic_maps_operator_vocabulary_pressure_v0.py`
3. `memory/research/symbolic-maps-level4/operator_vocabulary_pressure_v0.json`
4. `memory/research/symbolic-maps-level4/operator_vocabulary_pressure_v0_summary.md`
5. one result note with the pass decision.

---

## Immediate next action

Run the operator-vocabulary pressure pass now and decide whether the current frontier supports advance, hold, or demote.
