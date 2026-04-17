# Symbolic Maps Operator Canonicalization Probe Result v0

**Date:** 2026-04-16  
**Owner surface:** sandy-chaos  
**Status:** completed bounded pass  
**Targets:** `SC-CONCEPT-0006`

---

## Benchmark target

Test whether the current four-artifact operator labels can be mapped into the smallest plausible canonical operator vocabulary for the active query families without heavy hand-translation.

The probe used one tiny canonical vocabulary spanning:
- `structural_normalization`
- `constraint_discipline`
- `comparison_reuse`

---

## Evidence reviewed

- `plans/symbolic_maps_operator_vocabulary_pressure_result_v0.md`
- `plans/symbolic_maps_operator_canonicalization_probe_v0.md`
- `memory/research/symbolic-maps-level4/normalization_sketch_v0.json`
- `memory/research/symbolic-maps-level4/operator_vocabulary_pressure_v0.json`
- `memory/research/symbolic-maps-level4/operator_canonicalization_probe_v0.json`
- `memory/research/symbolic-maps-level4/operator_canonicalization_probe_v0_summary.md`
- `scripts/symbolic_maps_operator_canonicalization_probe_v0.py`
- `tests/test_symbolic_maps_operator_canonicalization_probe.py`

---

## Result

The final probe came back **mixed but not terminal**.

Observed totals:
- direct mapped: **16/25** (`64%`)
- semantic mapped: **4/25** (`16%`)
- unmapped: **5/25** (`20%`)

Shared multi-artifact canonicals do exist in all three query families:
- `normalize` across 2 artifacts
- `constrain` across 2 artifacts
- `compose` across 2 artifacts
- `bridge` across 2 artifacts

That means the vocabulary is **not purely imposed**.
There is some real cross-artifact structure here.

But the probe still missed the success bar:
- direct lexical mapping stayed below the `70%` threshold,
- the shared canonicals are thin rather than broad,
- and several useful mappings still depend on arguable compression choices rather than plainly recurring operator language.

So the strongest supportable read is:

> `SC-CONCEPT-0006` still retains hardening candidacy in a weak, bounded sense,
> but it has not earned schema hardening,
> and the candidacy should now be considered parked rather than actively advancing.

---

## Failure conditions / falsification pressure

Do not revive hardening pressure unless later evidence improves at least one of these:

- direct lexical mapping rises above the current thin `64%` level,
- shared multi-artifact canonicals become broader than one or two artifacts each,
- operator labels start converging without needing interpretive compression.

If future passes still look like this, treat the lane as comparison-useful but not schema-hardenable.

---

## Decision

**HOLD, and demote active hardening pressure**

Concretely:
- keep `SC-CONCEPT-0006` as a real bounded comparison/result surface,
- do **not** advance toward schema hardening,
- and stop treating hardening as the next active proof move.

This is not a demotion of the concept itself.
It is a demotion of **hardening candidacy from the active next-step slot**.

---

## Immediate next action

Commit the current bounded proof package.
If the lane is revisited later, reopen from a new artifact or new naturally convergent vocabulary signal, not by pushing the current schema-harden route harder.
