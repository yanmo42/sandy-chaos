# Symbolic Maps Level-4 Benchmark v0

**Date:** 2026-04-06  
**Owner surface:** sandy-chaos  
**Status:** draft v0  
**Targets:** `SC-CONCEPT-0006`  
**Purpose:** define the first discriminating benchmark for symbolic maps / narrative invariants so the concept can be pressured as a Level-4 candidate rather than remaining only an artifact family.

---

## Why this exists

`SC-CONCEPT-0006` now has enough artifact weight to justify a stronger test.

What is still missing is a benchmark that can answer:

> Does the invariant-guided symbolic-maps approach produce more stable, reusable, inspectable structure than a looser symbolic-description baseline?

Until that question is pressured directly, the concept remains partly trapped at the "formalized artifact" level.

This benchmark is intended to move it toward **Discriminating Test** territory.

---

## Claim under test

### Primary claim

A symbolic-map artifact family backed by narrative invariants can extract more stable and reusable interpretive structure than looser symbolic description alone.

### What this does **not** claim yet

- that the symbolic-maps family is scientifically validated in general
- that it is the only useful interpretation layer
- that automation should promote it further without benchmark evidence
- that a schema alone proves conceptual value

---

## Benchmark question

Across a small but meaningful set of symbolic artifacts:

1. does invariant-guided extraction produce **higher cross-artifact consistency**?
2. does it produce **better round-trip reconstructability**?
3. does it produce **more complete inspectable structure**?
4. does it create **better downstream reuse value**?

If the answer is not meaningfully yes on at least one major axis, then the current stronger claims about symbolic maps should be softened or revised.

---

## Benchmark shape

## Input set

Use **three artifacts** from the existing symbolic-maps family or immediate near-neighbors.

### Proposed starting set

1. `docs/symbolic-maps/symbolic_maps_intelligence_modules.md`
2. `docs/symbolic-maps/symbolic_operator_extraction_naming.md`
3. one third related artifact chosen for comparability and structure diversity

### Selection rule for artifact 3

Choose an artifact that:
- clearly belongs to the same symbolic / interpretive family or sits immediately adjacent to it
- differs enough in style or emphasis to pressure the extraction method
- is not so distant that the comparison becomes meaningless

### Why only 3 artifacts in v0

- enough to test consistency instead of one-off interpretation
- small enough to execute manually
- forces focus on benchmark quality rather than corpus sprawl

---

## Comparison arms

## Arm A — Invariant-guided extraction

For each artifact, extract into a constrained structure.

### Required fields

- `artifact_id`
- `artifact_family`
- `symbolic_entities`
- `roles`
- `relations`
- `operators_or_transformations`
- `candidate_invariants`
- `constraints_or_boundaries`
- `failure_conditions`
- `reuse_candidates`

### Rule

The extraction must be concrete enough that another operator could inspect the output and compare it against outputs from the other artifacts.

### Non-goal

Do not let the schema become so elaborate that it wins only by vocabulary inflation.

---

## Arm B — Loose symbolic-description baseline

For each artifact, produce a plausible non-schema-bound symbolic reading.

### Expected contents

- freeform symbolic summary
- important motifs
- interpretive/narrative reading
- notable themes or tensions

### Rule

This baseline must be made in good faith.
It should be a competent loose symbolic interpretation, not a deliberately weak strawman.

---

## Scoring dimensions

## 1. Cross-artifact consistency

### Question

When similar structures appear across the three artifacts, does the method represent them in a stable and reusable way?

### Evaluation focus

- repeated entity naming consistency
- repeated relation consistency
- repeated operator/invariant consistency

### v0 scoring rubric

For each dimension:
- `0` = inconsistent / mostly ad hoc
- `1` = partial overlap / unstable naming
- `2` = strong stable overlap

### Why it matters

If the invariant-guided method cannot stabilize repeated structure better than loose interpretation, it is not yet earning its complexity.

---

## 2. Round-trip reconstructability

### Question

Given only the extracted output, can an operator reconstruct the core interpretive shape of the original artifact without depending on the original prose?

### v0 scoring rubric

- `0` = extraction loses the core structure
- `1` = partial reconstruction only
- `2` = preserves the main symbolic logic

### Why it matters

This tests whether the extraction actually carries structure rather than just compressing language.

---

## 3. Schema completeness

### Question

Does the extraction produce meaningfully filled structural fields rather than vague placeholders or null-heavy formality?

### Evaluation focus

- proportion of required fields filled meaningfully
- number of filler entries
- number of ambiguous catch-all entries

### v0 scoring rubric

- `0` = sparse / mostly filler
- `1` = partially complete
- `2` = meaningfully complete and inspectable

### Why it matters

A schema that produces empty ritual is not a real benchmark win.

---

## 4. Downstream reuse value

### Question

Can the extracted output be reused for later comparison, validation, naming work, or loader/validator development more effectively than the loose baseline?

### Evaluation focus

- easier cross-artifact comparison
- easier invariant reuse
- easier future validator/loader design
- clearer next-step formalization path

### v0 scoring rubric

- `0` = not meaningfully reusable
- `1` = partially reusable
- `2` = clearly reusable for follow-on work

### Why it matters

This is the practical payoff test.
The method should create leverage, not only prettier notes.

---

## Optional later dimension — inter-operator agreement

This is out of scope for the very first pass, but worth noting.

A stronger later version could compare two independent extractions of the same artifact and measure overlap.

That would test whether the invariant method is robust across operators rather than only coherent within one operator's mind.

---

## Failure condition

The benchmark should be treated as failed or inconclusive if any of the following happen:

- invariant-guided extraction shows no material advantage over the loose baseline
- the schema proves too rigid to capture the artifact family well
- the invariant method becomes technically neat but interpretively hollow
- added structure does not improve comparison, reconstruction, or reuse
- benchmark success depends mostly on operator sympathy rather than inspectable output quality

Failure is allowed.
A failed benchmark is still a useful outcome because it tells us the concept should be revised, narrowed, or held at Level 3.

---

## Minimal protocol

## Step 1 — finalize the three artifacts

Pick the third artifact and record why it belongs in the set.

## Step 2 — freeze the extraction structure

Use the required fields above and avoid changing them mid-run unless a defect is severe enough to invalidate the benchmark.

## Step 3 — run both arms on all three artifacts

For each artifact, produce:
- one invariant-guided extraction
- one loose symbolic baseline reading

## Step 4 — score both arms

Score each arm on:
- cross-artifact consistency
- round-trip reconstructability
- schema completeness
- downstream reuse value

## Step 5 — write result note

Summarize:
- where the invariant method won
- where it lost
- where the benchmark design itself needs revision
- whether `SC-CONCEPT-0006` should be considered closer to Level 4

---

## Deliverables

### Required v0 outputs

1. this benchmark spec
   - `plans/symbolic_maps_level4_benchmark_v0.md`

2. one extraction template or schema draft
   - likely markdown first, schema later if the method survives pressure

3. one result note
   - location TBD, likely under `memory/research/` or `plans/`

### Optional follow-on outputs

- a JSON schema if the extraction shape proves stable
- a validator/loader stub if reuse value is clearly demonstrated
- a pressure event updating `SC-CONCEPT-0006`

---

## Promotion rule

Do **not** treat benchmark completion alone as proof of concept maturity.

Promotion pressure should remain conservative:
- if the benchmark is weak → revise or hold
- if the benchmark shows clear advantage on multiple axes → consider stronger formalization
- if results are mixed → keep the concept in pressure-testing with a narrower next test

---

## v0 execution stance

Start manual-first.

This benchmark should begin as:
- human-readable
- inspectable
- low-overhead
- easy to fail honestly

Automation comes later only if the structure survives manual pressure.

---

## Immediate next action

Choose artifact 3 and draft the extraction template for Arm A.

That is the smallest real move that turns this benchmark from intention into an executable test.
