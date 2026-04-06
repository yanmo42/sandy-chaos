# Memory Utilization × Ygg Kernel Compatibility Plan v0

**Date:** 2026-04-03  
**Owner surface:** sandy-chaos  
**Status:** planning artifact  
**Purpose:** define a precise path for making memory more usable while staying compatible with the recent Ygg continuity microkernel direction and future portable/bootstrap deployment

---

## Executive summary

Yes: improving memory utilization is compatible with Ygg kernelization **if we keep the boundary clean**.

The right split is:

- **Ygg kernel** owns the minimal authoritative continuity substrate:
  - identity anchors
  - embodiment snapshot
  - active work state
  - structured event log
  - promotion queue
- **memory utilization layer** lives above that kernel as a **service / policy layer** that:
  - indexes,
  - ranks,
  - summarizes,
  - proposes promotion,
  - and answers memory-use questions.

That means memory utilization should be treated as a **kernel-adjacent service**, not fused into the microkernel itself.

If we do that, the system becomes:
- more portable,
- more bootstrappable,
- easier to install on new Linux environments,
- and less likely to rot into one giant non-portable brain blob.

---

## What "better memory" should mean

Not bigger memory.  
Not more files.  
Not a fancier archive.

The target capability is:

> given a prompt, restart, or active lane, surface the smallest set of memory artifacts that best improves the next decision.

That means the improved system should get better at:
- resume quality,
- next-action clarity,
- durable-decision recall,
- project-context reuse,
- and promotion of important traces into durable memory.

---

## Compatibility verdict with Ygg kernelization

### Short answer
**Compatible: yes.**  
**Should memory utilization be inside the kernel: no.**

### Why
The kernel spec already draws a narrow boundary around:
- active work state,
- structured events,
- promotion pipeline,
- identity/embodiment distinction,
- and boot/wake determinism.

Those are exactly the right primitives for a later memory-utilization service to consume.

This is already visible in the kernel surfaces now present:
- `state/ygg-kernel.json`
- `state/active-work.json`
- `state/event-queue.jsonl`
- `state/promotion-queue.jsonl`

Source: `memory/daily/2026-04-03.md#L37-L67`

### Boundary rule
The kernel should expose **authoritative state**.  
The memory utilization layer should expose **derived usefulness**.

That is the clean design.

---

## Architectural split

## Layer 0 — Kernel (authoritative continuity substrate)

Owned by Ygg microkernel.

### Responsibilities
- identity continuity
- embodiment refresh
- active-work authority
- event authority
- promotion-candidate authority
- deterministic wake/re-entry

### Canonical surfaces
- `core/YGG-KERNEL.md`
- `state/ygg-self.json`
- `state/ygg-kernel.json`
- `state/active-work.json`
- `state/event-queue.jsonl`
- `state/promotion-queue.jsonl`

### Rule
The kernel must remain small and stable.
It should not decide retrieval heuristics for every task class.

---

## Layer 1 — Memory Utilization Service

Kernel-adjacent, but not part of kernel authority.

### Responsibilities
- stratified retrieval
- active-memory indexing
- multi-factor ranking
- decision summaries
- memory-use benchmarks
- promotion recommendations
- compact operator-facing outputs

### Candidate outputs
- `state/active-memory-index.json`
- `state/recent-summary.json`
- `state/memory-query-cache.json`
- benchmark/evaluation artifacts under Sandy Chaos research

### Rule
All outputs here are **derived**.
If a derived artifact disagrees with authoritative kernel state, the kernel wins.

---

## Layer 2 — Application / project adapters

Project-specific or surface-specific use.

### Responsibilities
- repo-specific retrieval tuning
- surface-specific prompt packs
- planner/reporter hooks
- Discord / CLI / site / notebook integration
- research-lane adapters

### Rule
Adapters may consume memory summaries, but should not become hidden authorities.

---

## The surgical move: v1 implementation objective

The next real step should be:

> build a **memory query benchmark + derived active-memory index** that sits on top of the kernel surfaces and recent memory artifacts.

This is the smallest useful slice because it:
- improves real retrieval quickly,
- avoids premature complexity,
- pressure-tests the design on real questions,
- and keeps the kernel boundary intact.

---

## Precise implementation plan

## Phase 1 — Benchmark the actual memory questions

### Goal
Define what “better memory utilization” means in operational terms.

### Deliverable
- `memory/research/memory-utilization-v0/benchmark_queries_v0.json`

### Query classes
At minimum include:
- what were the last 2 big things we got done?
- what is the highest-leverage next move?
- what did we decide about X?
- what active lanes exist right now?
- what should be promoted from recent work?
- what prior concept work overlaps this new idea?
- what changed since the last wake/restart?

### Required fields per benchmark item
- `query_id`
- `prompt`
- `task_type`
- `expected_artifact_types`
- `expected_answer_fields`
- `must_include`
- `must_not_include`
- `gold_sources`
- `evaluation_notes`

### Why this comes first
Without benchmark questions, “memory improvement” will drift into architecture cosplay.

---

## Phase 2 — Define a derived active-memory index

### Goal
Create a compact machine-readable surface for “what matters now?”

### Proposed output
- `state/active-memory-index.json`

### Inputs
- `state/active-work.json`
- `state/promotion-queue.jsonl`
- recent daily notes
- durable memory
- recent research and planning artifacts
- recent event queue entries

### Suggested fields
- `updatedAt`
- `activeLanes`
- `recentMilestones`
- `openPromotionCandidates`
- `durableConstraints`
- `relatedArtifactsByTopic`
- `resumeRecommendations`

### Important rule
This file is a **cache / synthesis layer**, not the source of truth.

---

## Phase 3 — Retrieval policy with multiple modes

### Goal
Stop treating all retrieval as one semantic-search problem.

### Retrieval modes
- **recency mode** — what changed lately?
- **durable mode** — what stable preferences/decisions constrain the answer?
- **active-work mode** — what current lanes/tasks are relevant?
- **promotion mode** — what deserves distillation or promotion?
- **concept-overlap mode** — what prior notes/research already rhyme with this idea?
- **restart mode** — what do I need to know to resume competently after boot?

### Ranking factors
- semantic relevance
- recency
- importance
- project fit
- source authority
- active-lane linkage
- promotion status
- user-importance weighting

### Suggested output behavior
Return fewer artifacts with stronger rationale instead of many vaguely relevant snippets.

---

## Phase 4 — Minimal summary products

### Goal
Make resumption cheap.

### First two summary products

#### A. Wake / restart summary
Output:
- top recent changes
- active lane(s)
- next action(s)
- blocking issues
- candidate promotions

#### B. Task-context summary
Given a prompt, output:
- durable constraints
- active related work
- recent relevant milestones
- likely source artifacts
- omissions / uncertainty

### Design standard
Every summary should be:
- sourceable,
- compact,
- inspectable,
- and reproducible from authoritative state + clear retrieval logic.

---

## Phase 5 — Promotion routing improvements

### Goal
Make memory promotion less accidental.

### Additions
- candidate scoring rubric
- stale-candidate review rule
- promotion-target recommendations
- rejection/archival reasons

### Minimal durable promotion targets
- durable memory
- workflow note
- plan
- concept packet
- canonical doc

### Important distinction
The utilization layer should **recommend** promotion.  
The kernel should continue to **track** promotion candidates.

---

## Phase 6 — Package for portability / bootstrappability

### Goal
Ensure this can become an installable Linux-friendly subsystem rather than a one-machine tangle.

### Required portability rules

#### 1. Local-path independence
Do not bake `/home/ian/...` assumptions into the logic.
Use workspace-relative paths or a small config file.

#### 2. Kernel-first boot
A fresh install should be able to boot from:
- doctrine files,
- kernel schemas,
- empty or minimal state surfaces,
- and selective imported durable memory.

#### 3. Safe empty-state behavior
If memory files are sparse or absent, the system should still boot with:
- empty active-work state,
- empty event queue,
- empty promotion queue,
- and no broken retrieval assumptions.

#### 4. Derived-state rebuildability
`active-memory-index.json` and summaries must be rebuildable from authoritative sources.
They should never be the only place important facts live.

#### 5. Configurable adapters
Repo-specific tuning should live in adapters/config, not in core memory logic.

#### 6. Schema versioning
Version:
- kernel surfaces,
- active-memory index,
- benchmark schema,
- retrieval policy schema.

This matters if you want cross-machine portability and reproducible upgrades.

---

## Installable-system view

If the longer-term dream is “portable and bootstrappable as an installable system on Linux,” then the stack should eventually look like this:

### Package A — Ygg kernel
Contains:
- doctrine templates
- kernel schemas
- wake logic
- event model
- active-work state schema
- promotion queue schema
- Heimdall / Ratatoskr interfaces

### Package B — Memory utilization service
Contains:
- indexing logic
- retrieval modes
- summary generation
- benchmark harness
- evaluation harness
- optional lightweight CLI/report commands

### Package C — Project adapters
Contains:
- Sandy Chaos adapter
- future repo adapters
- project-specific ranking tweaks
- artifact discovery rules

That packaging is much more installable than trying to ship one fused assistant blob.

---

## Why this is better than putting memory logic into the kernel

If memory utilization goes into the kernel itself, several bad things happen:
- kernel bloat
- harder replication
- more upgrade fragility
- more cross-project contamination
- harder debugging of authority vs derivation
- difficulty booting from minimal state

If it stays a service:
- the kernel remains portable and reliable,
- memory logic can evolve faster,
- project adapters can remain optional,
- and a new install can come up cleanly even before advanced retrieval is configured.

---

## Claim tiers

### Defensible now
- Memory utilization should be built as a kernel-adjacent service, not fused into the Ygg microkernel.
- The current Ygg kernel surfaces are already a strong substrate for this work.
- A benchmark-first approach is the right surgical move.
- Portability improves when authoritative state and derived memory products remain separate.

### Plausible but unproven
- An active-memory index will materially improve restart quality and next-action clarity.
- Multi-mode retrieval will outperform semantic lookup alone on real continuity questions.
- This split will support an eventually installable Linux-friendly continuity stack with less fragility.

### Speculative
- This architecture could become a reusable general continuity/memory substrate beyond Sandy Chaos and current Ygg work.
- Promotion-aware retrieval may become a major strategic multiplier rather than just a convenience layer.

---

## Failure conditions

This plan fails if:
- the benchmark is weak or unrepresentative,
- the active-memory index becomes stale quickly,
- derived outputs start masquerading as authoritative truth,
- portability is claimed but paths/config remain machine-specific,
- or the implementation becomes more complex than the decision value it creates.

---

## Recommended immediate next 3 moves

1. **Create the benchmark query artifact**  
   `memory/research/memory-utilization-v0/benchmark_queries_v0.json`

2. **Define the schema for `state/active-memory-index.json`**  
   small, derived, rebuildable

3. **Implement one minimal summary path**  
   “what changed + what matters now + next action” from kernel state + recent memory

That is the cleanest path that is both useful now and compatible with the kernelization direction.

---

## Sources / alignment notes

- Ygg kernelization established the microkernel boundary and canonical state surfaces.  
  Source: `memory/daily/2026-04-03.md#L1-L67`
- Ygg kernel spec explicitly keeps continuity primitives in-kernel and planning/research logic out-of-kernel.  
  Source: `core/YGG-KERNEL.md`
- Prior planning artifact identified active work, stratified retrieval, summaries, promotion routing, and evaluation as the main memory-utilization pillars.  
  Source: `plans/memory-utilization-layer-v0.md`

---

## Provisional continuity contract

- **branch_outcome_class:** local
- **disposition:** TODO_PROMOTE
- **promotion_target:** workflow
- **next_action:** create a benchmark-first memory-utilization research bundle that consumes Ygg kernel surfaces without expanding the kernel boundary
