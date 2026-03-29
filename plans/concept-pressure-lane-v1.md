# Concept Pressure Lane v1

**Date:** 2026-03-29  
**Owner surface:** sandy-chaos  
**Purpose:** Convert one raw concept into a structured, pressure-tested, promotion-aware artifact with explicit uncertainty and failure logic.

---

## Why this matters

Sandy Chaos already has strong ideas and rich narrative framing. The current bottleneck is reliable conversion from idea-space to decision-space.

This lane exists to ensure every concept can answer:

1. What is the claim tier right now? (`defensible` / `plausible` / `speculative`)
2. What evidence exists today?
3. What would falsify or materially weaken the claim?
4. What test should happen next?
5. What should be promoted, revised, deferred, or killed?

Without this lane, architecture quality drifts toward confidence language. With this lane, we get inspectable progression.

---

## Scope (v1)

### In scope
- Single task class: **pressure-test one concept node**
- Single pass through: `planner -> builder -> verifier -> reporter -> disposition`
- Artifacts persisted under `spine/` + `plans/` + `templates/`
- One completed real run

### Out of scope
- Full automation orchestrator
- UI/graph front-end
- Multi-concept batch scheduling
- Proof-grade formalization requirements

---

## Task class contract

**Input:** one concept candidate (new or existing) with a short human prompt.  
**Output:**
- concept packet (`spine/concepts/*.yaml`)
- pressure event (`spine/pressure/YYYY-MM-DD/*.yaml`)
- run notes/report (optional, but recommended)
- explicit next action + next test

---

## Stage contracts

## 1) Planner
Produces structured framing:
- normalized concept name + summary
- lane and claim tier hypothesis
- missing assumptions
- failure conditions
- required evidence set
- next test proposal

**Fail if:** concept remains too vague to evaluate or lacks candidate falsification path.

## 2) Builder
Produces concrete artifacts:
- concept packet from template
- linked evidence paths
- pressure event draft

**Fail if:** required schema fields are absent or evidence references are non-existent.

## 3) Verifier
Checks quality gates:
- schema/structure validity
- claim tier coherence vs evidence
- failure conditions present and testable
- next test and next action are operational (not rhetorical)

**Fail if:** promotion/disposition is asserted without evidence and falsification framing.

## 4) Reporter
Produces short decision-useful output:
- what was tested
- what survived vs failed
- final disposition
- immediate next action

**Fail if:** summary cannot guide the next operator step within one read.

---

## Promotion/disposition rubric (v1)

- **KEEP_EXPLORING**: useful structure exists, but key tests still open
- **REVISE**: framing useful, current form has material flaws
- **NEEDS_FALSIFICATION**: concept could matter, but evidence is below promotion threshold
- **DOC_PROMOTE / CODE_PROMOTE / TEST_PROMOTE**: only when evidence supports durable movement
- **KILL**: claim no longer worth lane occupancy

Rule: promotion strength must be proportional to consequence.

---

## Artifact map

- `spine/concepts/SC-CONCEPT-XXXX.yaml`
- `spine/pressure/YYYY-MM-DD/SC-PRESSURE-YYYYMMDD-NN.yaml`
- `templates/spine_concept_packet_v1.yaml`
- `spine/schemas/concept.schema.json`

---

## v1 done criteria

v1 is complete when:
1. one concept passed full lane end-to-end,
2. all artifacts are persisted and inspectable,
3. disposition + next action + next test are explicit,
4. at least one lane defect/improvement is logged.

---

## Immediate next actions after v1

1. Compare disposition consistency across completed runs.
2. Tighten verifier warnings where ambiguity persists.
3. Decide which lane steps to automate first (likely verifier/reporter scaffolding).
4. Add lightweight evidence-strength scoring so link presence is not treated as sufficient support.

---

## Execution log (2026-03-29)

Completed in this session:
- Added lane spec (`plans/concept-pressure-lane-v1.md`).
- Added reusable concept packet template (`templates/spine_concept_packet_v1.yaml`).
- Added seed lane concept (`spine/concepts/SC-CONCEPT-0007.yaml`).
- Logged initial lane pressure run (`SC-PRESSURE-20260329-01`).
- Ran two follow-on lane passes for consistency:
  - `SC-PRESSURE-20260329-02` on `SC-CONCEPT-0003`
  - `SC-PRESSURE-20260329-03` on `SC-CONCEPT-0006`
- Extended concept schema/validator support for `missing_assumptions` + `next_test` and validated spine integrity with local scripts.
