# Symbolic Maps Level-4 Scoring Pass v0

**Date:** 2026-04-07  
**Owner surface:** sandy-chaos  
**Status:** active frontier follow-on  
**Targets:** `SC-CONCEPT-0006`  
**Depends on:** `plans/symbolic_maps_level4_benchmark_v0.md`, `plans/symbolic_maps_level4/comparison_note_v0.md`

---

## Purpose

Run the smallest honest follow-on to the first symbolic-maps Level-4 benchmark pass.

This note exists to answer one question:

> Does the apparent Arm A advantage survive explicit small-score pressure, or was the first comparison pass too soft?

This is a scoring pass, not a new benchmark family and not a schema/tooling buildout.

---

## Inputs

### Benchmark spec
- `plans/symbolic_maps_level4_benchmark_v0.md`

### Existing comparison note
- `plans/symbolic_maps_level4/comparison_note_v0.md`

### Artifact set
1. `plans/symbolic_maps_level4/extraction_01_symbolic_operator_extraction_naming.md`
2. `plans/symbolic_maps_level4/baseline_01_symbolic_operator_extraction_naming.md`
3. `plans/symbolic_maps_level4/extraction_02_rimuru_adaptive_substrate_snap_model.md`
4. `plans/symbolic_maps_level4/baseline_02_rimuru_adaptive_substrate_snap_model.md`
5. `plans/symbolic_maps_level4/extraction_03_symbolic_maps_intelligence_modules.md`
6. `plans/symbolic_maps_level4/baseline_03_symbolic_maps_intelligence_modules.md`

---

## Scoring dimensions

Use the same four dimensions already declared in the benchmark spec.

1. **Cross-artifact consistency**
2. **Round-trip reconstructability**
3. **Schema completeness / structural coverage**
4. **Downstream reuse value**

### Score scale
- `0` = weak / absent
- `1` = partial / mixed
- `2` = clear strength

Keep the scale small.
Do not introduce extra dimensions mid-pass unless a defect makes the current pass invalid.

---

## Evaluation shape

For each of the three artifacts:
- assign Arm A and Arm B a `0-2` score on each dimension
- add one short justification line per dimension

Then:
- total the scores by arm
- note where Arm A wins clearly, where it is mixed, and where Arm B is competitive

---

## Decision rule

### Confirmed partial support
Use this result if Arm A shows a real edge on multiple dimensions, especially:
- cross-artifact consistency
- structural coverage
- downstream reuse

### Mixed
Use this result if Arm A wins narrowly, inconsistently, or mostly by subjective interpretation.

### Failed or inconclusive
Use this result if explicit scoring cannot distinguish Arm A from Arm B in a meaningful way.

---

## Failure conditions

Treat the scoring pass as invalid or insufficient if:
- the existing benchmark dimensions cannot be applied cleanly to the current artifact set
- justifications collapse into taste-language rather than inspectable reasons
- the score outcome depends mostly on operator sympathy
- the scorecard reveals that the comparison note hid major ambiguity

---

## Output

Produce one short result note that states:
- total scores by arm
- strongest dimensions for Arm A
- dimensions that stayed mixed
- disposition for `SC-CONCEPT-0006`
- whether the next move should be:
  - another bounded benchmark pass, or
  - a narrow validator/schema follow-on, or
  - hold/revise

---

## Scorecard results

### Artifact 1 — Naming note

| Dimension | Arm A | Arm B | Notes |
| --- | --- | --- | --- |
| Cross-artifact consistency | 2 | 1 | Arm A preserves the mechanism/capability/artifact split in packet form; Arm B preserves the gist but lets those layers blur more easily across reuse. |
| Round-trip reconstructability | 2 | 2 | Both arms preserve the main logic of the source note well because the source is already compact and structurally explicit. |
| Schema completeness / structural coverage | 2 | 1 | Arm A captures operators, boundaries, failure modes, and reuse slots directly; Arm B folds much of that back into prose. |
| Downstream reuse value | 2 | 1 | Arm A is immediately more usable for validator/schema/comparison work; Arm B is mainly orientation-friendly. |

### Artifact 2 — Rimuru specimen translation

| Dimension | Arm A | Arm B | Notes |
| --- | --- | --- | --- |
| Cross-artifact consistency | 1 | 0 | Arm A preserves reusable roles like threshold crossing, coherence organizer, and metaphor/model/mechanism separation; Arm B keeps the story but is more specimen-specific and harder to align cleanly with the other artifacts. |
| Round-trip reconstructability | 2 | 2 | Both arms preserve the main transition pattern and caution against overclaiming mechanism. |
| Schema completeness / structural coverage | 1 | 1 | This is the hardest artifact for both arms; Arm A is more structured, but the source intentionally leaves several boundaries unresolved. |
| Downstream reuse value | 1 | 0 | Arm A is at least reusable for threshold-taxonomy and future benchmark framing; Arm B remains mostly a vivid intuition carrier. |

### Artifact 3 — Modules roadmap

| Dimension | Arm A | Arm B | Notes |
| --- | --- | --- | --- |
| Cross-artifact consistency | 2 | 1 | Arm A stabilizes modules, roles, ordering, and failure conditions in a form that lines up well with Artifact 1; Arm B keeps the high-level logic but drifts more in structural vocabulary. |
| Round-trip reconstructability | 2 | 2 | Both arms preserve the roadmap’s main operational demand clearly. |
| Schema completeness / structural coverage | 2 | 1 | Arm A preserves module dependencies, constraints, and failure conditions more inspectably. |
| Downstream reuse value | 2 | 1 | Arm A is directly stronger for implementation planning, comparison infrastructure, and future validator framing. |

---

## Totals

### By artifact

| Artifact | Arm A | Arm B |
| --- | --- | --- |
| Naming note | 8 | 5 |
| Rimuru specimen translation | 5 | 3 |
| Modules roadmap | 8 | 5 |
| **Total** | **21** | **13** |

### By dimension

| Dimension | Arm A | Arm B |
| --- | --- | --- |
| Cross-artifact consistency | 5 | 2 |
| Round-trip reconstructability | 6 | 6 |
| Schema completeness / structural coverage | 5 | 3 |
| Downstream reuse value | 5 | 2 |

---

## Interpretation

The explicit score pass sharpens the earlier qualitative judgment rather than overturning it.

### Confirmed
- Arm A has a real advantage in **cross-artifact consistency**.
- Arm A has a real advantage in **structural coverage**.
- Arm A has a real advantage in **downstream reuse**.

### Mixed
- **Round-trip reconstructability** does **not** distinguish the arms in this three-artifact set.
- This matters because it limits what can honestly be claimed: Arm A is not simply “better at recovering meaning.” Its strength is in producing a more reusable and comparison-friendly packet.

### Why this matters
The result supports a narrower, more defensible claim:

> Narrative-invariant / symbolic-map extraction currently earns its keep by stabilizing comparison structure, preserving boundaries, and increasing downstream reuse, not by universally outperforming loose symbolic reading on raw interpretive recovery.

---

## Result

- **result:** partial-support confirmed
- **disposition:** KEEP_EXPLORING
- **promotion posture:** still not ready for broad promotion

`SC-CONCEPT-0006` should remain active, but the lane should stay under bounded pressure rather than moving directly into schema/validator hardening.

---

## Recommended next move

Prefer **one more bounded benchmark pass** over immediate schema hardening.

Reason:
- the scoring pass confirms a real advantage,
- but the evidence is still coming from only three artifacts,
- and the weakest case in the set is also the most specimen-heavy one.

So the next clean pressure move is:
- extend the benchmark with a small additional artifact or small heterogeneous follow-on set,
- check whether the same Arm A advantage survives,
- and only then decide whether validator/schema hardening is justified.

A narrow validator/schema follow-on should happen **only if** the next bounded pass reveals one precise structural slot that clearly deserves hardening.

---

## Scope guard

Do **not** use this pass to:
- expand the corpus broadly
- build loaders or validators yet
- rewrite the benchmark family broadly
- reopen frontier ranking unless the lane collapses under scoring

This pass exists to sharpen the current frontier, not to escape it.
