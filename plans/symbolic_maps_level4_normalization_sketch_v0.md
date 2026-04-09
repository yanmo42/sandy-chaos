# Symbolic Maps Level-4 Normalization Sketch v0

**Date:** 2026-04-09  
**Owner surface:** sandy-chaos  
**Status:** active frontier bounded follow-on  
**Targets:** `SC-CONCEPT-0006`  
**Depends on:** `plans/symbolic_maps_level4_scoring_pass_v1.md`

---

## Purpose

Land the smallest technical follow-on recommended by the four-artifact scoring pass:

> express the repeated `role / operator / constraint / failure / boundary` skeleton in one tiny normalization draft and test whether it covers the current benchmark set without expanding into schema theater.

This pass is intentionally narrow.
It is not a general symbolic-maps ratification and not a command to build a large validator stack.

---

## What was added

### Code surface
- `nfem_suite/intelligence/narrative_invariants/benchmark.py`
- `scripts/symbolic_maps_normalization_sketch_v0.py`

### Bounded benchmark data
- `memory/research/symbolic-maps-level4/normalization_sketch_v0.json`

### Evidence artifacts
- `memory/research/symbolic-maps-level4/normalization_sketch_v0_summary.json`
- `memory/research/symbolic-maps-level4/normalization_sketch_v0_summary.md`

### Tests
- `tests/test_symbolic_maps_normalization_sketch.py`

---

## Benchmark rule

The pass counts as support only if the current four benchmark artifacts can all be expressed with the same five slot families:

1. `role_slots`
2. `operator_slots`
3. `constraint_slots`
4. `failure_slots`
5. `boundary_slots`

without introducing repeated ad hoc extra families just to rescue coverage.

---

## Result

### Support achieved, but bounded

The current four-artifact set does fit the same minimal slot family.

Observed summary:
- artifact count: `4`
- fully populated artifacts: `4/4`
- no extra rescue field families were required
- the semi-structured atlas still fits the same skeleton as the three prose/architecture/specimen artifacts

That is enough to say:

> the repeated comparison skeleton is real enough to survive one minimal formalization pass.

It is **not** enough to say:
- a global symbolic-maps schema is now validated,
- future artifacts will fit without revision,
- or broad validator hardening should begin immediately.

---

## Why this matters

This move upgrades the frontier from:
- manual benchmark notes only

to:
- one tiny executable normalization surface with validation and repeatable summary output.

That is a real proof-path move because it turns a repeated manual observation into a bounded inspectable artifact.

---

## Failure condition for this lane

Reject or revise this sketch if either of these starts happening:
- new artifacts repeatedly require ad hoc slot-family expansion,
- or the sketch fails to improve comparison leverage over the prose benchmark notes.

---

## Recommended next action

Do one more bounded follow-on:

- test whether the normalization sketch helps answer a small set of cross-artifact comparison queries more cleanly than the prose extractions alone.

If it does not, keep the pass as a useful compression artifact but do not escalate it into larger schema work.
