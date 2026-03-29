# Topological Memory for Continuity Retrieval (v0)

## Status
Research draft

## Date
2026-03-27

## Concept origin
Ian

## Developed with
Ian + Solace/Nyx-assisted structuring, pressure-testing, and workflow support

## Scope
A bounded investigation into whether topology-aware external memory retrieval over the current environment/ecosystem outperforms flatter retrieval methods for continuity tasks.

## Non-scope
This draft does **not** claim:
- that memory is fundamentally spatial in a physical or ontological sense,
- that this explains consciousness,
- that this establishes a subatomic-to-cosmic theory,
- or that geometric metaphor is itself mechanism.

## Working thesis
Meaningful events in an active ecosystem may be better recovered when memory is modeled as traces distributed across a structured topology rather than as isolated stored content.

In this framing:
- **nodes** = repos, files, docs, commits, checkpoints, channels, sessions, threads, artifacts
- **edges** = explicit relations such as `promotes_to`, `derived_from`, `mentioned_in`, `checkpointed_by`, `depends_on`, `resumes`
- **traces** = weighted, decaying event residues written onto nodes/edges
- **retrieval** = path-based traversal over the topology rather than flat lookup alone

## Architecture role split
- **Sandy Chaos** is the research/model engine that asks: *does this compute intelligently?*
- **Ygg** is the control/continuity shell for **planned coordination across temporal frames**. It should expose checkpoint/query/promotion surfaces around validated mechanisms rather than duplicate the research engine.
- **Ravens** are bounded scouting/review processes commissioned by Ygg. Because they can gather evidence and touch bounded state, their outputs must return through Ygg for adjudication before any durable promotion.

## Governance invariant
- Amoeba can propose and explore.
- Ravens can inspect and may touch bounded state.
- Ygg commissions, receives returns, adjudicates, and controls promotion.
- Durable repo/docs/workflow surfaces should only change through explicit promotion paths.

## Amoeba execution surface
Amoeba is the **pre-promotional exploratory membrane** in the execution stack.
It is not just a vibe label and not a canonical promotion surface.
Its job is to absorb weak signals, unfinished tensions, weird mechanism sketches, raw captures, and intermediate residues **before** they are compressed into durable routing or canon.

Within this framing:
- `morph-00-gradients` = tensions, attractors, unfinished potentials
- `morph-10-flow-computer` = mechanism design, theory shaping, and execution-shaping operator sketches
- `morph-20-metabolism` = transformation work over raw inputs, fragments, and captures
- `morph-30-traces` = residues that may later become retrievable continuity structure

Amoeba should preserve generativity while still exposing explicit disposition.
It exists so exploratory motion does not collapse into either random sludge or premature governance.

### Amoeba disposition semantics
- **DROP_LOCAL** = let the local exploratory result dissolve
- **LOG_ONLY** = keep as trace, no escalation
- **TODO_PROMOTE** = candidate for task-stack promotion
- **DOC_PROMOTE** = candidate for repo/docs formalization
- **POLICY_PROMOTE** = candidate governance invariant or workflow rule
- **ESCALATE** = route upward for adjudication

## Core research question
Does topology-aware continuity retrieval outperform simpler baselines in the current ecosystem?

## Win condition
The geometry must pay rent.

This direction wins only if topology-aware retrieval beats at least one flatter baseline on bounded continuity tasks **and** produces inspectable paths explaining why an artifact, checkpoint, or next action surfaced.

## Initial success criterion
The approach should beat at least one or more of:
- keyword search
- tag search
- recency heuristic
- embedding retrieval

on bounded continuity tasks such as:
- what should be resumed next,
- where a concept came from,
- which artifact should be promoted,
- which prior durable trace is most relevant.

## Claim tiers

### Defensible now
- A topology-aware external memory graph over the current environment is buildable.
- Trace decay + weighted path retrieval is a coherent modeling approach.
- This can be benchmarked against flatter retrieval baselines.

### Plausible but unproven
- Promotion/disposition metadata will improve continuity retrieval quality.
- Path-based retrieval over trace-bearing topology may outperform flat retrieval on bounded ecosystem tasks.
- A useful invariant may exist here that transfers across multiple continuity/routing problems.

### Speculative
- The same operator may scale beyond software ecosystems into broader cognitive/physical analogies.
- "Geodesic memory" may become more than an interface metaphor.

## Failure conditions
This direction fails if:
- it cannot beat simple baselines,
- path outputs are not interpretable,
- the graph becomes too dense or arbitrary,
- trace dynamics require too many ungrounded knobs,
- or the idea remains elegant metaphor without computational leverage.

## First bounded experiment
Build a benchmark of ~30 real continuity queries drawn from the current environment.

For each query, compare:
- keyword baseline
- recency baseline
- embedding baseline (if available)
- topological memory model

Score:
- retrieval accuracy
- usefulness
- path interpretability
- promotion/routing quality

## V0 schema freeze (2026-03-28)
Task #1 is now frozen as explicit machine contracts:

- Graph contract: `schemas/topological_memory_graph_v0.schema.json`
- Benchmark query contract: `schemas/topological_memory_queries_v0.schema.json`
- Seed examples:
  - `templates/topological_memory_graph_v0.example.json`
  - `templates/topological_memory_queries_v0.example.json`

### Freeze boundaries
- **Schema version strings are fixed** for v0 (`topological-memory-v0`, `topological-memory-queries-v0`).
- **Node/edge/trace objects are closed** (`additionalProperties: false`) to avoid silent drift.
- **Trace disposition vocabulary is explicit** (`DROP_LOCAL`, `LOG_ONLY`, `TODO_PROMOTE`, `DOC_PROMOTE`, `POLICY_PROMOTE`, `ESCALATE`).
- **Time fields use ISO date-time strings** for deterministic replay and evaluation windows.
- **Weights are normalized to `(0, 1]`** for simple baseline comparability.

Any semantic expansion beyond these contracts should be treated as a v1 proposal, not a silent v0 mutation.

## Research discipline
- model first, mechanism second, metaphor last
- touch the repo, not the stars
- no promotion to canonical docs without benchmark evidence
- no ontology claims from retrieval wins alone

## Provenance note
This concept was originated by Ian on 2026-03-27 and bounded into its current benchmark-first research framing through Ian + Solace/Nyx collaboration.
