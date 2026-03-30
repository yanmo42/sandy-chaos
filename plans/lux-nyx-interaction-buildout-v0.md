# Lux–Nyx Interaction Buildout v0

**Date:** 2026-03-30  
**Owner surface:** sandy-chaos  
**Purpose:** turn the Lux–Nyx interaction grammar into a small, testable Sandy Chaos surface instead of leaving it as a symbolic note only

---

## Why now

The symbolic note is strong enough to preserve, but not yet strong enough to canonize.

What it has earned:
- bounded archive status,
- a typed interaction contract draft,
- a subsystem record,
- a membrane record,
- and a code-side loader / validation surface so future implementation work starts from explicit artifacts.

What it has **not** yet earned:
- canonical architecture status,
- runtime authority,
- or broad claims about intelligence/governance improvement.

---

## Build objective

Create a narrow interaction layer that can answer:

1. what kind of input arrived,
2. which Nyx transforms are allowed,
3. what shadow artifact must be emitted,
4. what trace must be preserved,
5. and how success/failure will be measured.

---

## v0 artifact set

This pass should leave behind:

- `docs/archive/lux_nyx_interaction_contract_v0.md`
- `spine/membranes/interpretive-governance-v1.yaml`
- `spine/subsystems/SC-SUBSYSTEM-0003-lux-nyx-interaction-v0.yaml`
- `templates/lux_nyx_interaction_contract_v0.example.json`
- `nfem_suite/intelligence/narrative_invariants/lux_nyx_contract.py`
- tests for the minimal loader / validator surface

That gives the concept:
- one interpretive contract,
- one governance membrane,
- one subsystem identity,
- one typed code artifact,
- and one example payload.

---

## Recommended implementation phases

## Phase 0 — artifact stabilization

Done when:
- the contract exists,
- the subsystem exists,
- the membrane exists,
- the code scaffold loads example records,
- and validation/tests pass.

This phase is about **shape**, not intelligence.

## Phase 1 — manual evaluation path

Add a small evaluator that takes a Lux input record and produces a bounded recommendation:
- keep
- compress
- archive
- route
- hold
- promote-candidate
- refuse-with-reason

No automation heroics yet. The first version can be deterministic and rules-based.

## Phase 2 — suggestion-surface pilot

Apply the contract to one narrow real surface:
- next-action suggestion shaping

Minimal outcome:
- classify input
- choose allowed Nyx ops
- emit shadow artifact
- capture trace record

## Phase 3 — governance coupling

Only after the pilot is useful:
- connect contract outcomes to archive-vs-canonical routing,
- bind higher-risk pathways to declared evidence requirements,
- and ensure refusals / delays emit inspectable artifacts.

---

## Candidate code touchpoints

These are candidate integration surfaces, not commitments:

### 1. `nfem_suite/intelligence/narrative_invariants/`
Best home for the first typed artifact scaffold.

Why:
- already hosts symbolic/operator extraction artifacts,
- already has minimal typed-record patterns,
- and is close to the interpretive layer this concept belongs to.

### 2. `nfem_suite/intelligence/cognition/idea_field.py`
Possible future integration point if Lux input weighting starts shaping idea distributions or sampling priorities.

### 3. archive / promotion workflows
Possible future integration point if the contract begins to affect:
- archive routing,
- promotion gating,
- and bounded visibility decisions.

---

## Explicit non-goals for v0

Do **not** do these yet:
- do not claim a full interaction engine exists,
- do not bind this directly into runtime behavior,
- do not treat symbolic style as evidence of system value,
- do not make canonical docs depend on Lux/Nyx yet,
- do not allow silent gating without trace artifacts.

---

## Success criteria for later today

A good follow-on build session should produce at least one of:

1. a rules-based evaluator for Lux/Nyx records,
2. a trace artifact writer,
3. a first pilot on next-action suggestion shaping,
4. or a promotion-routing adapter using the contract fields.

---

## Failure conditions

The buildout should be reconsidered if:
- the record schema feels ornamental rather than decision-useful,
- operators cannot be made explicit enough for rules-based handling,
- no measurable pilot surface emerges,
- or the concept creates more narrative flourish than operational clarity.

---

## Tightest version of the spine

> Build Lux–Nyx first as a typed interaction contract with traces, then prove it on one pilot surface before granting it any larger architectural authority.
