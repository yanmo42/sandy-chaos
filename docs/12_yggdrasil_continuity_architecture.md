# 12 Yggdrasil Continuity Architecture

> **Status:** canonical architecture note for continuity and branching work.
>
> This document explains how **Yggdrasil** fits into Sandy Chaos as a continuity layer over the existing OpenClaw substrate. It is not a replacement for `FOUNDATIONS.md`, `WORKFLOW.md`, or the core theory docs. It sits beside them and explains how branching work is supposed to remain coherent over time.
>
> Related docs:
>
> - `FOUNDATIONS.md`
> - `WORKFLOW.md`
> - `docs/07_agentic_automation_loop.md`
> - `docs/09_research_automation_protocol.md`
>
> Claim posture:
>
> - **Defensible now:** Sandy Chaos already operates across multiple sessions, artifacts, tools, and cadences; explicit continuity rules reduce drift risk.
> - **Plausible but unproven:** making Yggdrasil explicit will improve project velocity and reduce context loss.
> - **Speculative:** broader analogies to organisms, societies, and generalized intelligence laws are useful, but should not do mechanism-level work by themselves.

---

## 1) Why this doc exists

Sandy Chaos now has enough moving parts that continuity has become an architectural problem, not just an organizational one.

The repo already supports:

- theory work,
- simulation and implementation work,
- validation and falsification work,
- automated loops,
- multiple OpenClaw sessions/lanes,
- and a growing set of durable artifacts.

What was still under-specified was how all of these local processes are supposed to relate to one another over time.

This document names that missing layer: **Yggdrasil**.

Yggdrasil is the continuity architecture for branching work. Its purpose is to let many local processes exist without losing a coherent center.

### Failure condition

If Sandy Chaos can sustain long-running multi-session, multi-surface work with low context loss and low drift **without** explicit continuity rules, then the architectural weight placed on Yggdrasil is overstated.

---

## 2) What Yggdrasil is

Yggdrasil is not a new physics theory. It is not a substitute for the project's causal or mathematical foundations. It is also not just a metaphor.

In repo terms, Yggdrasil is a practical architecture for deciding:

- what stays local,
- what becomes durable,
- what gets promoted into canonical surfaces,
- and how branching processes remain related to one another.

The architecture becomes necessary because OpenClaw already makes branching work easy:

- sessions can split,
- tasks can fork,
- notes and transcripts can accumulate,
- automation can run on different cadences,
- and artifacts can be produced in many places.

Those are strengths, but they also introduce drift risk. Yggdrasil is the layer that tries to keep branching work legible and governable.

### Plain-language definition

**Yggdrasil is a continuity model for branching intelligence.**
It gives the system a spine, allows branches, and defines how branch outputs may or may not alter the durable center.

---

## 3) Core primitives

### 3.1 Spine

The **spine** is the set of repo surfaces that should change slowly and only under stronger evidence or clearer intent.

In Sandy Chaos, spine-adjacent surfaces currently include:

- `FOUNDATIONS.md`
- canonical docs under `docs/`
- long-horizon workflow rules in `WORKFLOW.md`
- stable config and automation contracts under `config/`
- tests and validation surfaces when they define or enforce project behavior

The spine is where local results stop being merely contextual and start shaping the ongoing identity of the project.

### 3.2 Branch

A **branch** is any bounded local process allowed to unfold with relative independence.

Examples:

- a research session,
- a build session,
- a local refactor,
- an automation cycle,
- a dated research artifact bundle,
- a speculative note,
- a validation pass,
- a temporary exploratory script.

Branches are not errors. They are where variation appears.

### 3.3 Promotion

**Promotion** is the process by which a local branch result is evaluated before it alters more durable project surfaces.

A promotion decision answers questions like:

- should this stay local?
- should it be logged but not made authoritative?
- should it become a TODO?
- should it become canonical documentation?
- should it modify a hard contract or policy surface?

### 3.4 Durable trace

A **durable trace** is any artifact that can carry continuity across time.

Examples:

- transcript-derived summaries,
- notes in `memory/`,
- docs updates,
- config changes,
- tests,
- falsification reports,
- research-cycle artifacts,
- commit history.

Durability alone is not promotion. A durable trace can exist without being canonical.

### 3.5 Trust / provenance

Once work is distributed, **trust** becomes structural.

In this context, trust means:

- provenance is clear,
- evidence is inspectable,
- affected surfaces are explicit,
- reversibility or rollback is understood,
- and the consequence level matches the evidence level.

### 3.6 Temporal scale

Distance from the spine is also a temporal variable.

- edge branches may run faster, cheaper, and more provisionally,
- spine-adjacent changes should move more slowly and with higher evidentiary burden.

This is not a metaphorical flourish. It is an operating rule.

---

## 4) Mapping Yggdrasil into Sandy Chaos

### 4.1 Edge / fast-loop surfaces

These are places where rapid variation is acceptable:

- short-lived sessions,
- temporary implementation branches,
- exploratory scripts,
- scratch notes,
- local falsification attempts,
- provisional prompts/contracts,
- early automation-cycle outputs.

Expected behavior:

- fast iteration,
- low promotion pressure,
- high reversibility,
- explicit willingness to discard.

### 4.2 Bridge / meso-loop surfaces

These surfaces compare, summarize, or route multiple local results:

- daily/meso reviews,
- research-cycle bundles,
- orchestrator plans and summaries,
- digest artifacts,
- TODO updates,
- verification summaries.

Expected behavior:

- summarize branch outputs,
- route what matters,
- suppress noise,
- decide whether stronger promotion is justified.

### 4.3 Spine / slow-loop surfaces

These are durable project-shaping surfaces:

- `FOUNDATIONS.md`
- canonical docs in `docs/`
- long-lived workflow rules in `WORKFLOW.md`
- stable automation/config contracts
- tests that encode hard behavioral expectations

Expected behavior:

- low-frequency change,
- stronger evidence burden,
- clear provenance,
- explicit rationale and rollback path.

---

## 5) Continuity rules

### Rule 1 — No silent meaningful branch outcomes

If a branch produces a meaningful result, it should not simply vanish.

Meaningful results include:

- external effects,
- evidence-bearing validation outcomes,
- policy-relevant findings,
- durable design decisions,
- new blockers or next actions.

Such a branch should end with an explicit disposition.

### Rule 2 — Use explicit dispositions

Recommended disposition classes:

- `DROP_LOCAL` — scratch/exploration with no durable consequence
- `LOG_ONLY` — preserve for traceability, but do not promote
- `TODO_PROMOTE` — create or update tactical work item
- `DOC_PROMOTE` — update canonical explanation/design docs
- `POLICY_PROMOTE` — update hard contract/workflow/config
- `ESCALATE` — human review or unresolved conflict needed

### Rule 3 — Promotion burden rises with consequence

The more durable the target surface, the stronger the burden should be.

A local note can tolerate ambiguity.
A TODO should name a concrete next action.
A canonical doc update should explain the claim and the reason for promotion.
A foundations/config change should carry explicit evidence and rollback awareness.

### Rule 4 — Durable surfaces should not be overwritten by metaphor

Metaphor can orient. It cannot substitute for mechanism.

Nervous-system, tree, society, and lineage analogies are useful only when they clarify the architecture rather than bypass its evidentiary burden.

### Rule 5 — Temporal cadence is part of the design

Fast loops belong at the edge.
Meso loops compare and route.
Slow loops consolidate.

If everything runs at one cadence, the system either becomes noisy or rigid.

---

## 6) Relationship to existing Sandy Chaos machinery

Yggdrasil does not replace the existing planner / builder / verifier / reporter lanes. It provides a continuity interpretation for them.

A useful mapping is:

- **planner** → branch creation / routing / promotion candidate framing
- **builder** → local variation / implementation / experiment
- **verifier** → evidence filter and promotion gate pressure
- **reporter** → durable trace generation and cross-time continuity

Likewise, the existing fast / meso / slow cadence maps naturally onto:

- **fast** → edge sensing and local adaptation
- **meso** → routing, summarization, and comparison
- **slow** → consolidation, policy shaping, and long-horizon continuity

This means Yggdrasil should be understood as an integrative architecture over mechanisms the repo already has.

---

## 7) Near-term implementation implications

The architecture becomes real only when it changes operating behavior.

Near-term implications:

1. branch outcomes should carry an explicit disposition,
2. orchestrator/task artifacts should distinguish local vs promotable outputs,
3. context carry across sessions should become easier and more consistent,
4. canonical promotion targets should be clearer (`docs/`, `WORKFLOW.md`, `FOUNDATIONS.md`, `plans/todo.md`, tests/config),
5. automation summaries should report what was learned and where it landed.

### Failure condition

If these additions create more overhead than coherence, the implementation should be simplified rather than defended for its own sake.

---

## 8) Open questions

The following remain open:

- How much disposition structure is enough before it becomes bureaucracy?
- Which branch classes deserve automatic logging vs explicit manual promotion?
- How should transcript/session continuity best map into repo-local durable traces?
- Which promotion decisions are safe to automate, and which should remain human-gated?
- How far should the nervous-system analogy be taken before it stops clarifying and starts obscuring?

These questions are part of the architecture, not proof that it has failed.

---

## 9) Summary

Yggdrasil is the continuity architecture for branching work in Sandy Chaos.

It assumes that:

- branching is necessary,
- local variation is useful,
- durable continuity does not happen automatically,
- trust and provenance matter once work is distributed,
- and temporal cadence should differ by consequence.

In practice, it gives Sandy Chaos a way to keep many local processes alive without letting the whole project lose its center.
