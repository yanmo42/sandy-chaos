# Memory Utilization Layer v0

**Date:** 2026-04-03  
**Owner surface:** sandy-chaos  
**Status:** planning artifact  
**Purpose:** turn existing memory into a usable decision substrate rather than a passive archive

---

## Why this exists

The immediate bottleneck is probably **not memory creation**.
It is **memory utilization**.

We already have:
- daily memory traces,
- curated durable memory,
- research artifacts,
- concept packets,
- continuity state,
- active project notes.

The problem is that these are not yet consistently converted into the forms that matter most at action time:
- what is active now,
- what matters for this task,
- what changed recently,
- what is durable and decision-relevant,
- what should be promoted,
- what can be safely ignored.

The goal of this layer is to improve:
- restart continuity,
- task resumption,
- concept reuse,
- decision speed,
- and project-wide leverage from already-created artifacts.

---

## Core objective

Build a memory utilization layer that can answer, quickly and reliably:

1. **What are we actively doing right now?**
2. **What important things happened recently?**
3. **What durable preferences/decisions should constrain this task?**
4. **What prior artifacts are relevant to this exact prompt?**
5. **What deserves promotion, demotion, summarization, or retirement?**

If it cannot answer those better than naive file search, it is not working.

---

## Problem statement

### Current failure modes

- Important material exists but remains buried in daily logs.
- Retrieval is too dependent on semantic similarity rather than task-role relevance.
- Recency and importance are not consistently separated.
- Promotion candidates may exist without decisive routing.
- “What matters now?” is still partly reconstructed from scratch each session.
- Strong ideas may be remembered but not operationally surfaced.
- Memory overhead can increase token/use cost without proportional decision gain.

### The actual target

Not “more memory.”  
Not “better embeddings” alone.  
Not “perfect knowledge graph” prematurely.

The target is:

> a compact, inspectable, action-oriented system that routes the right memory into the right task at the right time.

---

## v0 design stance

Memory utilization should stay **small, practical, and inspectable**.

Start with a narrow stack:
- active work extraction,
- memory stratification,
- multi-factor retrieval,
- decision summaries,
- promotion routing.

Do **not** begin with:
- giant ontology commitments,
- universal auto-tagging fantasies,
- fully autonomous memory curation,
- or public-facing theory claims.

---

## Proposed memory strata

### 1) Ephemeral / session-local
For immediate conversational continuity and short-lived context.

Examples:
- recent messages
- temporary task states
- intermediate notes

### 2) Recent working memory
For “what has happened lately and what is active?”

Examples:
- daily memory files
- active-work surfaces
- current project notes
- current blockers / open loops

### 3) Durable operational memory
For stable decisions, preferences, norms, architecture choices.

Examples:
- curated MEMORY.md
- continuity contracts
- platform defaults
- lane policies
- user preferences

### 4) Research / concept memory
For reusable intellectual artifacts and pressure-tested conceptual work.

Examples:
- research bundles
- concept packets
- falsification notes
- synthesis artifacts
- simulation plans

### 5) Promotion / decision memory
For artifacts that are candidates to become policy, docs, workflows, or active commitments.

Examples:
- promotion queue
- doc-promotion candidates
- todo-promotions
- workflow changes

---

## Five capability pillars

## Pillar 1 — Active Work Extraction

### Goal
Produce a compact, trustworthy answer to:
> what are the active lanes right now?

### Required outputs
- active lane list
- current blockers
- next actions
- recency score
- importance score
- owner surface / project
- status (`active`, `blocked`, `dormant`, `candidate`)

### Candidate sources
- `state/active-work.json`
- recent daily notes
- current plan files
- recent research cycle artifacts
- promotion queue items with unfinished disposition

### Success condition
A human or agent should be able to resume the correct work in under one minute.

---

## Pillar 2 — Stratified Retrieval

### Goal
Retrieve memory by **role**, not just by resemblance.

### Retrieval modes
- **recency mode** — what changed recently?
- **durable mode** — what stable preferences / decisions matter?
- **task-relevance mode** — what prior artifacts help solve this prompt?
- **active-work mode** — what does this affect in current lanes?
- **promotion mode** — what is waiting to be distilled or advanced?

### Ranking factors
- semantic relevance
- recency
- importance
- promotion status
- project fit
- task type match
- source trust level

### Success condition
The system consistently returns fewer, better, more decision-useful artifacts than naive search.

---

## Pillar 3 — Decision Summaries

### Goal
Generate compact summaries that reduce resumption friction.

### Candidate summary products
- last 3 meaningful moves
- current active lanes
- what changed since last wake
- memory relevant to this prompt
- promotion candidates awaiting action
- unresolved blockers

### Design rule
These summaries must be:
- short,
- inspectable,
- sourceable,
- and immediately useful.

### Success condition
Summaries reduce resume time and lower the need for repeated reconstruction.

---

## Pillar 4 — Promotion Routing

### Goal
Move information to the right level of permanence.

### Routing questions
- should this stay in daily memory?
- should it become durable memory?
- should it become a plan?
- should it become a concept packet?
- should it become a canonical doc?
- should it be dropped?

### Minimal dispositions
- `LOG_ONLY`
- `TODO_PROMOTE`
- `DOC_PROMOTE`
- `WORKFLOW_PROMOTE`
- `MEMORY_PROMOTE`
- `DROP_LOCAL`

### Success condition
Important decisions stop getting trapped in logs.

---

## Pillar 5 — Evaluation / Pressure Tests

### Goal
Test whether memory utilization is actually improving work.

### Benchmark task types
- “What were the last 2 big things we got done?”
- “What should we work on next?”
- “What already exists related to this concept?”
- “What did we decide about X?”
- “What should be promoted from recent work?”

### Metrics
- retrieval precision at small k
- resume time
- number of omitted critical facts
- number of irrelevant artifacts surfaced
- user-rated usefulness
- promotion hit-rate

### Success condition
The layer beats current ad hoc retrieval on real tasks.

---

## v0 artifact package

### 1) Planning artifact
This file.

### 2) Query set
Create a benchmark set of real memory-use questions.

Suggested file:
- `memory/research/memory-utilization-v0/benchmark_queries_v0.json`

### 3) Evaluation note
Track retrieval performance and failure cases.

Suggested file:
- `memory/research/memory-utilization-v0/evaluation_v0.md`

### 4) Optional schema surfaces
If needed, define small inspectable surfaces like:
- `state/active-memory-index.json`
- `state/promotion-candidates.json`
- `state/recent-summary.json`

Do this only if they materially reduce overhead.

---

## Minimal implementation order

## Phase 1 — requirements capture
Define the real query classes that matter most.

Deliverables:
- benchmark queries
- query categories
- expected answer fields

## Phase 2 — active-work index
Build or refine a compact active-work surface.

Deliverables:
- active lane schema
- current lane extraction rules
- blocker / next-action rules

## Phase 3 — retrieval policy
Implement ranking logic that mixes:
- relevance,
- recency,
- importance,
- promotion state,
- project fit.

Deliverables:
- retrieval mode definitions
- ranking heuristic spec
- failure cases

## Phase 4 — summary generator
Create one or two minimal summary products.

Deliverables:
- current active lanes summary
- last meaningful moves summary

## Phase 5 — pressure test
Run the benchmark questions and compare against baseline retrieval.

Deliverables:
- evaluation note
- improvement recommendations
- promote / revise / kill decision

---

## How this connects to existing Sandy Chaos work

### Research automation protocol
This should behave like a bounded research/verification cycle, not a vibes-only architecture essay.

### Concept pressure lane
Memory utilization itself can be pressure-tested as a concept with:
- claim tier,
- falsification path,
- next experiment,
- and disposition.

### Topological memory retrieval work
That work should inform this effort, but not dominate it too early.

Topological retrieval may become one retrieval engine among several.
The real target is decision-useful routing, not graph complexity for its own sake.

### Ygg / continuity kernel work
Ygg should likely **use** this layer.
Sandy Chaos should likely **research and pressure-test** it.

That preserves the current architecture split:
- Sandy Chaos = research/model/meaning engine
- Ygg = continuity/control substrate

---

## Claim tiers

### Defensible now
- Existing memory is underutilized relative to its potential value.
- Retrieval / routing / promotion are likely higher-leverage bottlenecks than raw memory creation alone.
- A small memory utilization layer would likely improve continuity, planning, and resumption quality.

### Plausible but unproven
- A multi-factor retrieval policy will outperform naive semantic lookup alone.
- Active-work extraction may provide disproportionate leverage compared with more ambitious memory architectures.
- Summary products may reduce token cost and resumption friction materially.

### Speculative
- A compact utilization layer could become a general high-leverage control primitive across multiple repos/surfaces.
- Promotion-aware retrieval may substantially improve strategic decision quality rather than only retrieval convenience.

---

## Failure conditions

This plan fails if:
- it adds more maintenance burden than decision value,
- active-work extraction remains stale or untrustworthy,
- retrieval does not outperform simple file search or semantic search,
- summaries become too lossy to guide action,
- or the project drifts into knowledge-graph theater without operational gains.

---

## Recommended immediate next action

Create the benchmark query artifact first.

Why:
- it forces the system to define what “better memory utilization” actually means,
- it prevents premature architecture drift,
- and it gives the later retrieval layer a concrete pressure-test harness.

Suggested next file:
- `memory/research/memory-utilization-v0/benchmark_queries_v0.json`

---

## Provisional continuity contract

- **branch_outcome_class:** local
- **disposition:** TODO_PROMOTE
- **promotion_target:** workflow
- **next_action:** create a benchmark set of real memory-use questions and expected answer fields before designing retrieval/index machinery
