# Sandy Chaos Spine

The spine is the repo's central authority for **concept state**, **pressure outcomes**, and **promotion/disposition decisions**.

It exists to answer:
- what concepts currently matter
- how strong their claims are
- what evidence, code, and tests touch them
- what happened after pressure-testing
- where they should land next

## Core objects

### 1. Concept nodes
Tracked units of meaning/evolution.

Stored in: `spine/concepts/*.yaml`

Each concept should declare at least:
- identity (`id`, `name`, `summary`)
- lane + tags
- claim tier and lifecycle status
- links to docs/code/tests
- failure conditions
- missing assumptions (when known)
- next test + next action
- promotion target

### 2. Pressure events
Records of meaningful evaluation cycles.

Stored in: `spine/pressure/YYYY-MM-DD/*.yaml`

A pressure event captures:
- what concept(s) were evaluated
- what kind of pressure occurred
- what evidence was involved
- what survived / failed
- final disposition
- next action

### 3. Promotion ledger
Chronological record of durable promotions/demotions.

Stored in: `spine/promotions/ledger.jsonl`

Each entry records:
- which concept(s) moved
- from/to status
- promotion target
- rationale/basis
- resulting disposition

## Lifecycle model

### Claim tiers
- `defensible`
- `plausible`
- `speculative`

### Status values
- `seed`
- `draft`
- `pressure-testing`
- `validated-partial`
- `canonical`
- `archived`
- `deprecated`
- `killed`

Claim tier and status are separate.
A concept can be `plausible + pressure-testing` or `defensible + canonical`.

## Disposition classes

Current working set:
- `KEEP_EXPLORING`
- `REVISE`
- `ARCHIVE`
- `DOC_PROMOTE`
- `CODE_PROMOTE`
- `TEST_PROMOTE`
- `MERGE_INTO_EXISTING`
- `YGG_BRIDGE`
- `NEEDS_FALSIFICATION`
- `WAITING_ON_EVIDENCE`
- `KILL`

These dispositions are intended to complement the broader branch disposition language in `WORKFLOW.md` / `FOUNDATIONS.md`.

## Design rules

1. Track **concepts**, not every file.
2. Do not backfill the whole repo at once.
3. Start with the concepts carrying the most architectural weight.
4. Every meaningful pressure cycle should end with an explicit disposition.
5. Canonical promotion requires evidence proportionate to consequence.
6. If a concept's long-term home is Ygg, record that as a promotion target rather than letting Sandy Chaos absorb it indefinitely.

## Seed scope

The initial spine tracks a small set of high-leverage concepts:
- nested temporal domains
- cognitive tempo orchestration
- hyperstition policy attractor dynamics
- topological memory continuity retrieval
- symbolic maps / narrative invariants
- Ygg continuity disposition model

## Format note

The current spine files intentionally use a **simple constrained YAML/JSONL style** so they can be parsed by lightweight local tooling.

That means: prefer flat fields plus simple lists, and avoid richer YAML features unless the parser is upgraded deliberately.

## Templates

Starter template for new concept packets:

- `templates/spine_concept_packet_v1.yaml`

## Reports

Use the helper scripts:

```bash
python3 scripts/spine_report.py
python3 scripts/spine_validate.py
```

- `spine_report.py` gives a quick status summary
- `spine_validate.py` checks structural integrity and broken references

It currently prints:
- concept counts by status / claim tier / lane
- concepts missing tests or failure conditions
- concepts that appear Ygg-bound

This is intentionally small. The goal is to create a durable center first, then make it smarter.
