# Symbolic Maps Level-4 Schema Hardening Gate v0

**Date:** 2026-04-16  
**Owner surface:** sandy-chaos  
**Status:** active frontier bounded follow-on  
**Targets:** `SC-CONCEPT-0006`  
**Depends on:** `plans/symbolic_maps_level4_normalization_sketch_v0.md`

---

## Purpose

Run one bounded gate on the current `SC-CONCEPT-0006` frontier artifacts and answer a narrower question than the normalization sketch itself:

> Is the repeated `role / operator / constraint / failure / boundary` skeleton now strong enough to justify schema hardening, or is it still only strong enough to justify bounded comparison pressure?

This pass is deliberately narrow.
It does **not** add new slot families, broaden the corpus, or ratify a larger symbolic-maps schema.

---

## Benchmark target

Use only the current four-artifact frontier package and the existing normalization sketch to test one hardening-relevant property:

> Do the current slot values show enough repeated cross-artifact convergence to support hardening, rather than merely enough repeated slot-family presence to support comparison?

The benchmark pressures convergence, not coverage.
Coverage already passed in `plans/symbolic_maps_level4_normalization_sketch_v0.md`.

---

## Evidence to review before evaluation

1. `state/ygg/active-work.json`
2. `spine/concepts/SC-CONCEPT-0006.yaml`
3. `plans/symbolic_maps_level4_benchmark_v1.md`
4. `plans/symbolic_maps_level4_scoring_pass_v1.md`
5. `plans/symbolic_maps_level4_normalization_sketch_v0.md`
6. `memory/research/symbolic-maps-level4/normalization_sketch_v0.json`
7. `memory/research/symbolic-maps-level4/normalization_sketch_v0_summary.md`
8. `plans/symbolic_maps_level4/extraction_04_starter_atlas.md`
9. `plans/symbolic_maps_level4/baseline_04_starter_atlas.md`

---

## Pre-evaluation success, failure, and ambiguity conditions

### Success condition
Treat the pass as strong enough to justify schema hardening only if **all** of the following hold:

1. At least **three** of the five existing slot families show repeated cross-artifact convergence in their **values**, not only in their presence.
2. The convergence is visible without adding rescue fields, synonym tables, or broad manual reinterpretation.
3. At least one of the convergent families is structurally central to later hardening work, such as `operator_slots`, `constraint_slots`, or `boundary_slots`, rather than convergence appearing only in warning-language or generic failure rhetoric.

### Failure condition
Treat the pass as **not** strong enough for schema hardening if **any** of the following hold:

1. Slot-family coverage remains high, but slot-value convergence is sparse or mostly artifact-local.
2. Repeated signals depend mainly on generic negative language or scaffold words rather than stable reusable vocabulary.
3. Hardening would require inventing a taxonomy or controlled vocabulary that is not already earned by the current four-artifact frontier.

### Ambiguity condition
Treat the pass as ambiguous if:

1. one or two families look promising, but the convergence is not broad enough yet,
2. overlap appears only after aggressive normalization or hand interpretation,
3. or the current sketch looks good for comparison but still underpowered for schema decisions.

---

## Method

1. Use the existing normalization sketch only.
2. Normalize slot text minimally:
   - lowercase,
   - split into simple word tokens,
   - ignore short tokens and obvious scaffold terms.
3. Measure whether each slot family shows repeated non-scaffold token reuse across artifacts.
4. Treat this as a hardening gate, not as a theory test.

This is intentionally strict.
A family can be useful for comparison and still fail a hardening gate.

---

## Deliverables

1. This benchmark note.
2. `scripts/symbolic_maps_schema_hardening_gate_v0.py`
3. `memory/research/symbolic-maps-level4/schema_hardening_gate_v0.json`
4. `memory/research/symbolic-maps-level4/schema_hardening_gate_v0_summary.md`
5. one result note recording the advance / hold / demote decision.

---

## Promotion guard

Do **not** harden the schema just because the current four-artifact set fits one repeated slot family.

Hardening is only justified if the slot **values** themselves are becoming stably reusable across artifacts.
If the current signal is mostly structural resemblance plus manual interpretation, keep the lane under bounded pressure.

---

## Immediate next action

Run the hardening gate on the current normalization sketch and decide whether `SC-CONCEPT-0006` should advance toward schema hardening, hold under bounded pressure, or demote.
