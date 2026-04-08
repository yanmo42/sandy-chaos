# Symbolic Maps Level-4 Benchmark v1

**Date:** 2026-04-08  
**Owner surface:** sandy-chaos  
**Status:** active frontier follow-on  
**Targets:** `SC-CONCEPT-0006`  
**Supersedes:** `plans/symbolic_maps_level4_benchmark_v0.md`

---

## Purpose

Run the next bounded benchmark pass for `SC-CONCEPT-0006` without escaping the active frontier.

This pass exists to answer one narrower question than v0:

> Does the Arm A advantage in consistency, structural coverage, and downstream reuse survive when the artifact set becomes slightly more heterogeneous, rather than remaining limited to three prose-heavy notes?

This is still a bounded follow-on, not a corpus expansion and not a validator/schema buildout.

---

## Why artifact 4 was needed

The first pass and explicit scoring pass were strong enough to keep the lane alive, but still narrow in one important sense:
- all three artifacts were human-readable notes,
- two were fairly prose-forward,
- and even the more specimen-like case remained a markdown translation note.

That means the next honest pressure move is not broader theory. It is a slightly more heterogeneous source object that still belongs to the same symbolic-maps family.

---

## Chosen artifact 4

### Artifact 4
- `docs/symbolic-maps/examples/starter_atlas.json`

### Why this is the right follow-on

It satisfies the v0 selection rule well:
- it clearly belongs to the symbolic-maps family,
- it differs from the earlier notes in representation and granularity,
- it pressures whether the invariant-guided method is genuinely reusable,
- it remains bounded and inspectable.

### Why it is more discriminating

This artifact is already semi-structured.
That matters because it creates a harder test for Arm A.

If Arm A only looked strong because it imposed structure on loose prose, then a semi-structured atlas should reduce its apparent advantage.
If Arm A still adds value here, the value is more likely to be real and reusable rather than just formatting theater.

---

## Updated artifact set

1. `docs/symbolic-maps/symbolic_operator_extraction_naming.md`
2. `docs/symbolic-maps/rimuru_adaptive_substrate_snap_model.md`
3. `docs/symbolic-maps/symbolic_maps_intelligence_modules.md`
4. `docs/symbolic-maps/examples/starter_atlas.json`

---

## Benchmark pressure for v1

The four dimensions remain unchanged:

1. cross-artifact consistency
2. round-trip reconstructability
3. schema completeness / structural coverage
4. downstream reuse value

Do not add new dimensions yet.
The goal is comparability with the earlier pass.

---

## What artifact 4 should pressure specifically

### 1. Cross-artifact consistency
Can Arm A align atlas fields like role, operators, constraints, failure modes, and composability with the invariant packets produced for the earlier notes?

### 2. Structural coverage
Can Arm A preserve not only the atlas rows, but also the implied structural slots that matter for later comparison, such as role type, operator family, constraint pattern, and exclusion boundaries?

### 3. Downstream reuse
Does Arm A produce a packet that is more reusable for future comparison, normalization, loader design, or taxonomy pressure than a fair loose baseline reading of the same atlas?

### 4. Round-trip reconstructability
This may remain mixed.
If the loose baseline reconstructs the atlas well, that is acceptable.
The discriminating pressure is still mainly on consistency, coverage, and reuse.

---

## Decision rule for the follow-on

### Stronger support
Use this result if Arm A still shows a real edge on at least two of these three dimensions:
- cross-artifact consistency
- schema completeness / structural coverage
- downstream reuse value

### Mixed
Use this result if the semi-structured atlas collapses most of Arm A’s advantage and leaves only marginal gains.

### Weakening signal
Use this result if the atlas reveals that Arm A is mostly rephrasing existing structure without adding meaningful comparison or reuse leverage.

---

## Failure conditions

Treat the follow-on as weakening or inconclusive if:
- artifact 4 is too different to compare meaningfully,
- Arm A adds almost no value over the baseline on the atlas,
- the perceived advantage comes mostly from formatting inflation,
- or the four-artifact set no longer points clearly to the same underlying invariant family.

---

## Deliverables for this pass

1. this note
   - `plans/symbolic_maps_level4_benchmark_v1.md`
2. Arm A artifact 4 extraction
   - `plans/symbolic_maps_level4/extraction_04_starter_atlas.md`
3. Arm B artifact 4 baseline
   - `plans/symbolic_maps_level4/baseline_04_starter_atlas.md`
4. one short follow-on scoring note
   - `plans/symbolic_maps_level4_scoring_pass_v1.md`

---

## Promotion guard

Do **not** move into validator/schema hardening just because artifact 4 is structured JSON.

Only move toward hardening if this pass reveals:
- one stable structural slot,
- used repeatedly across the set,
- whose hardening would create real comparison or validation leverage.

Otherwise keep the lane in bounded benchmark pressure.

---

## Immediate next action

Compare Arm A and Arm B on `starter_atlas.json`, then run one short four-artifact scoring pass to see whether the earlier Arm A advantage survives the more heterogeneous set.
