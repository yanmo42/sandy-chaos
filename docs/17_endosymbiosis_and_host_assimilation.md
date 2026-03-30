# Endosymbiosis and Host Assimilation in Sandy Chaos

## Status
Draft v0

## Document role
Canonical design/governance bridge for subsystem admission and architectural assimilation.

This document is intended to do three things:

1. define when a merged subsystem counts as part of the host architecture,
2. specify the records and contracts needed to make that status inspectable,
3. constrain how subsystem authority enters runtime and governance.

It is **not** a replacement for `FOUNDATIONS.md`, and it does not by itself grant promotion.

## Scope and compatibility

### In scope
- subsystem status vocabulary
- admission gates
- registry record expectations
- membrane contract expectations
- host-identity consequences for architecture decisions

### Out of scope
- replacing formal proof obligations
- proving theory claims directly
- promoting speculative language to canonical truth
- silently changing runtime behavior without governance pathways

### Compatibility with Foundations
This document adds an architectural classification layer on top of the hard contract in `FOUNDATIONS.md`.

That means:
- hard constraints and claim discipline still come from `FOUNDATIONS.md`
- subsystem canonicalization here must still be grounded in **F/C/E** evidence where relevant
- speculative language may guide design attention, but not override admissibility markers or promotion rules

## Purpose
This document defines a coherent design lens for Sandy Chaos after the recent convergence of multiple branch lineages into `main`.

The goal is not to use biological metaphor for ornament. The goal is to make a specific architectural problem legible:

**When a new subsystem is merged into the repository, under what conditions has it actually become part of the host architecture rather than merely being co-located with it?**

That is the endosymbiosis question.

---

## 1. Why this question matters now

Recent merges introduced at least five distinct lineages into `main`:

- temporal predictive processing bridge
- topological memory v0
- dispatch hardening
- hyperstition control corridor
- spine governance v1

These are not all the same kind of thing. Some are interpretive, some operational, some experimental, some governant, some infrastructural.

The repository therefore appears to be shifting from a collection of related research and tooling efforts into a **host architecture** with differentiated subsystems.

This creates a real design problem:

- What is the host?
- What functions are core?
- What counts as a subsystem versus an experiment?
- What must be true for a merged lineage to be considered canonical?
- How do we prevent beautiful but weakly-integrated branches from becoming architectural parasites?

---

## 2. Design stance

### Defensible now
A subsystem is not fully integrated just because its files are present in `main`.

### Defensible now
Architectural assimilation requires:
- a clear host function
- stable interfaces
- legible inputs and outputs
- governance status
- dependency relationships
- bounded influence on other subsystems

### Plausible but unproven
Treating merged subsystems as symbionts/organelle candidates may help guide cleaner architecture and clearer promotion decisions.

### Speculative
A sufficiently mature host model could support adaptive admission rules resembling biological integration pressure rather than static software categorization.

---

## 3. Core principle

**Merge is not assimilation.**

A merged lineage has only been assimilated when the host can describe and use it in the host's own causal grammar.

That means the host must be able to answer:
- What function does this subsystem serve?
- What does it consume?
- What does it produce?
- Who governs it?
- Who depends on it?
- What breaks if it is removed?
- What limits its authority?

If those answers are missing, the subsystem may still be valuable, but it is not yet fully part of the body.

---

## 4. Working host model for Sandy Chaos

Sandy Chaos can currently be interpreted as a host architecture with five interacting layers:

1. **Interpretive layer**
   - explanatory frames
   - theory bridges
   - conceptual doctrine

2. **Memory layer**
   - continuity storage
   - structured retrieval
   - inspectable recall paths

3. **Circulatory layer**
   - orchestration
   - scheduling
   - runtime dispatch

4. **Experimental layer**
   - simulations
   - exploratory cognition machinery
   - corridor or pressure probes

5. **Governance layer**
   - concept formalization
   - validation
   - pressure accumulation
   - promotion and legitimacy

This model is useful because it distinguishes classes of subsystem by host function rather than by branch origin.

### 4.1 Host layers mapped to current repo lanes

To avoid introducing a parallel ontology, these host layers should map onto the repo's existing workflow and automation lanes.

- **Interpretive layer** ↔ theory lane / canonical docs / conceptual compression
- **Memory layer** ↔ continuity retrieval / memory artifacts / inspectable recall infrastructure
- **Circulatory layer** ↔ ops lane / orchestration / scheduling / runtime dispatch
- **Experimental layer** ↔ simulation lane / corridor probes / bounded exploratory systems
- **Governance layer** ↔ validation lane / pressure accumulation / promotion and legitimacy machinery

This mapping matters because a subsystem is not embedded merely by being described well; it is embedded when its host layer and lane participation are both legible.

---

## 5. Endosymbiosis matrix

### 5.1 Temporal Predictive Processing Bridge
- **Lineage:** theory / interpretive framework
- **Biological role:** membrane doctrine / sensemaking epithelium
- **Host function served:** provides explanatory structure for temporal cognition, continuity, and prediction
- **Consumes:** conceptual ambiguity, prior theory fragments, framing pressure
- **Produces:** explanatory vocabulary, bridge concepts, interpretive constraints
- **Governed by:** research norms and document discipline more than executable validation
- **Depended on by:** potentially many systems; currently few operational consumers are evident
- **Assimilation status:** merged, weakly assimilated
- **Symbiosis class:** commensal → mutualistic candidate
- **Main risk:** becomes theology rather than constraint
- **Membrane/interface needed:** map theory terms into schema fields, runtime metrics, or governance criteria
- **Assimilation proof condition:** real downstream decisions explicitly cite and instantiate the framework

### 5.2 Topological Memory v0
- **Lineage:** retrieval / continuity / memory research
- **Biological role:** memory organelle candidate
- **Host function served:** path-structured retrieval and continuity recall
- **Consumes:** graph structures, benchmark queries, memory artifacts, retrieval prompts
- **Produces:** retrieval paths, scores, comparison reports, inspectable memory structures
- **Governed by:** research validation and promotion gate artifacts
- **Depended on by:** poised to support continuity, planning, and recall, but not yet clearly host-critical
- **Assimilation status:** strongly merged, partially assimilated
- **Symbiosis class:** incipient organelle
- **Main risk:** remains a high-quality enclave rather than standard infrastructure
- **Membrane/interface needed:** direct consumers in orchestration, reporting, or governance
- **Assimilation proof condition:** standard host workflows call and rely on topological retrieval outputs

### 5.3 Dispatch Hardening
- **Lineage:** orchestrator/runtime reliability
- **Biological role:** circulatory/autonomic regulation
- **Host function served:** stable execution flow and safer automation scheduling
- **Consumes:** scheduled tasks, config, runtime triggers
- **Produces:** more reliable dispatch behavior and execution semantics
- **Governed by:** operational/runtime constraints
- **Depended on by:** all automation lanes needing dependable execution
- **Assimilation status:** highly assimilated in function, lightly articulated in doctrine
- **Symbiosis class:** proto-organelle
- **Main risk:** critical but conceptually under-described
- **Membrane/interface needed:** explicit tie between runtime execution and governance semantics
- **Assimilation proof condition:** scheduling decisions are legible in the same ontology as pressure/promotion decisions

### 5.4 Hyperstition Control Corridor
- **Lineage:** experimental cognition / frame-aware simulation
- **Biological role:** exploratory sensory organ / mutation chamber
- **Host function served:** probes generative state-space under controlled experimental conditions
- **Consumes:** frames, phase assumptions, entropy/control dynamics, experimental prompts
- **Produces:** simulation results, corridor analyses, experimental evidence
- **Governed by:** experimental discipline and test coverage more than host-wide selection rules
- **Depended on by:** future conceptual work; direct runtime dependence is unclear
- **Assimilation status:** merged, intentionally semi-detached
- **Symbiosis class:** mutualistic symbiont
- **Main risk:** draws architecture toward itself before proving host benefit
- **Membrane/interface needed:** strict boundary between exploratory output and canonical/promotable output
- **Assimilation proof condition:** corridor results become one bounded evidence stream among others, not an oracle

### 5.5 Spine Governance v1
- **Lineage:** concept governance / validation / promotion workflow
- **Biological role:** skeleton + regulatory ledger
- **Host function served:** formalizes concepts, pressure, validation, and promotion legitimacy
- **Consumes:** concept packets, pressure events, validation inputs, promotion decisions
- **Produces:** ledgers, reports, validated artifacts, promotion history, legitimacy structure
- **Governed by:** its own schemas, validators, and workflow discipline
- **Depended on by:** potentially all canonical concept evolution
- **Assimilation status:** strongly merged, structurally central, not yet fully host-dominant
- **Symbiosis class:** strong organelle candidate / proto-skeletal core
- **Main risk:** governance theater without runtime consequence
- **Membrane/interface needed:** direct coupling to runtime behavior, research promotion, and concept survival rules
- **Assimilation proof condition:** subsystems increasingly must pass through spine semantics to count as canonical host development

---

## 6. Major missing membranes

The host is present in outline, but several membranes are still missing.

### 6.1 Theory ↔ Governance membrane
Questions:
- Which theory claims can affect promotion or validation?
- Which remain interpretive only?

Need:
- a translation layer between conceptual doctrine and admissible governance signals

### 6.2 Memory ↔ Dispatch membrane
Questions:
- Can automation retrieve continuity before acting?
- Can scheduling incorporate structured memory outputs?

Need:
- operational consumers of retrieval artifacts

### 6.3 Experiment ↔ Governance membrane
Questions:
- How do experimental outputs become admissible evidence?
- What blocks exploratory systems from gaining unearned authority?

Need:
- explicit evidence classes and promotion thresholds

### 6.4 Governance ↔ Runtime membrane
Questions:
- Can validated concepts change host behavior?
- Can runtime events feed back into pressure and promotion state?

Need:
- a closed loop between legitimacy and execution

Without these membranes, the repository contains co-located structures rather than fully vascularized architecture.

---

## 7. Canonical assimilation rules (proposed)

A merged subsystem should be treated as **canonical host architecture** only when all of the following are true:

1. **Host function clarity**
   - The subsystem serves a clearly named host function.

2. **Boundary clarity**
   - Inputs, outputs, and responsibility boundaries are explicit.

3. **Governance placement**
   - Its authority status is known: experimental, advisory, infrastructural, or canonical.

4. **Dependency legibility**
   - Upstream and downstream dependencies are visible.

5. **Failure legibility**
   - The host can state what degrades or fails if the subsystem is removed.

6. **Metabolic participation**
   - At least one standard host workflow consumes the subsystem's outputs.

7. **Constraint compatibility**
   - The subsystem does not require a contradictory ontology to justify its operation.

8. **Bounded influence**
   - Its sphere of authority is explicit, especially for experimental systems.

If these conditions are not met, the subsystem may still be valuable, but it should be classified as:
- experimental symbiont
- incubating organelle candidate
- auxiliary tool
- or archived lineage

not yet canonical host tissue.

---

## 8. Recommended subsystem statuses (v0)

### Canonical-core candidates
- dispatch hardening
- spine governance v1

### Near-core / organelle-candidate
- topological memory v0

### Interpretive but underbound
- temporal predictive processing bridge

### Experimental symbiont
- hyperstition control corridor

These statuses are not final truths. They are design positions to guide interface decisions.

---

## 9. The design problem to solve

The key unresolved question is:

**What is the host, and what are the admission rules for becoming part of its body?**

A useful working answer is:

> Sandy Chaos is a host architecture for inspectable recursive cognition work under explicit governance.

If that is accepted, then every merged subsystem must justify itself relative to that host identity.

Not every valuable branch becomes an organ.
Not every organ begins as canonical.
Not every experiment should be metabolized.

The design problem is therefore not only to invent subsystems, but to define:
- host identity
- admission criteria
- membrane rules
- legitimacy pathways
- deprecation and archival rules

---

## 10. Working answer: what the host is

A stronger working definition is needed if this document is to govern real design decisions.

### Proposed host identity

> **Sandy Chaos is a runtime for concept evolution under inspectable governance.**

This definition is preferred over weaker alternatives because it preserves the distinct roles of:
- variation generation
- continuity and memory
- runtime execution
- legitimacy and promotion
- theory as compression rather than sovereign truth

### Why this framing is currently strongest

#### Defensible now
The repository already contains machinery for:
- concept formalization
- pressure accumulation
- promotion logic
- continuity retrieval
- runtime execution
- simulation/experimental generation

That means the system is no longer well-described as only a research notebook or only an automation rig.

#### Plausible but unproven
The architecture may converge on a governed cognition engine whose primary unit of adaptation is the concept or concept-cluster.

#### Speculative
The host could eventually exhibit a meaningful concept-metabolism loop in which pressure, memory, experimentation, execution, and governance recursively shape one another.

### Consequence of this host definition

If the host is a runtime for concept evolution under inspectable governance, then:
- governance is not optional ornament
- experiments do not self-legitimate
- theory does not outrank validated operational evidence
- memory is not archival; it is continuity infrastructure
- runtime dispatch is not just convenience plumbing; it is metabolic flow

---

## 11. Admission protocol for merged subsystems

This section converts the metaphor into an operational decision rule.

### 11.1 Lifecycle classes

Every major subsystem should be assigned one of the following host statuses:

1. **Experimental**
   - generates candidate signals, artifacts, or exploratory results
   - cannot autonomously alter canonical host state
   - may influence later review, but only through declared evidence pathways

2. **Advisory**
   - may influence interpretation, planning, review, or routing recommendations
   - does not directly change canonical runtime or governance state without mediation
   - must declare what kind of advice is admissible and what remains non-binding

3. **Infrastructural**
   - provides host-critical capability relied upon by standard workflows
   - carries stronger compatibility, stability, and failure-legibility expectations
   - may affect runtime operation, but only within declared authority boundaries

4. **Canonical**
   - recognized as part of the host's body
   - integrated into normal legitimacy and execution pathways
   - permitted to alter standard host state through approved governance and runtime routes

### 11.1.1 Authority reminder

Merge presence, conceptual glamour, and author preference are not authority classes.

Every subsystem must declare:
- what kinds of outputs it may emit,
- what those outputs are allowed to influence,
- what they are explicitly not allowed to influence without mediation.

### 11.2 Admission gates

A subsystem advances toward canonical status by passing the following gates.

#### Gate A — Host function declaration
The subsystem must name the host function it serves.

Required output:
- function name
- concise purpose statement
- non-goals

#### Gate B — Boundary declaration
The subsystem must define what it consumes and produces.

Required output:
- input classes
- output classes
- ownership boundary
- failure surface

#### Gate C — Authority declaration
The subsystem must declare what kind of authority it has.

Allowed authority classes:
- experimental
- advisory
- infrastructural
- canonical-candidate

No subsystem may silently escalate authority by popularity, conceptual glamour, or merge presence.

#### Gate D — Dependency declaration
The subsystem must identify:
- what it depends on
- what depends on it
- whether removal would degrade or break standard workflows

#### Gate E — Workflow participation
At least one standard host workflow must consume the subsystem's outputs.

Without this, the subsystem remains a co-located enclave.

#### Gate F — Governance compatibility
The subsystem must be placeable within host governance:
- what evidence it produces
- what claims it may support
- what promotion or demotion consequences it can trigger

#### Gate G — Membrane definition
The subsystem must specify the contracts that regulate its interaction with adjacent layers.

### 11.3 Canonicalization rule

A subsystem should only be considered **canonical host tissue** when:
- Gates A-G are passed at acceptable quality, and
- its authority class has been explicitly acknowledged by governance.

---

## 12. Subsystem registry schema (proposed)

To make the architecture inspectable, each major subsystem should have a compact registry record.

### Proposed artifact placement

This schema becomes operational only if it lives somewhere concrete. A minimal path would be:

- `spine/subsystems/README.md` — registry conventions
- `spine/subsystems/<subsystem_id>.yaml` — one file per major subsystem

If that location changes later, the important part is preserving a stable, queryable home for subsystem identity and authority.

### Proposed fields
- `subsystem_id`
- `name`
- `status` — experimental | advisory | infrastructural | canonical
- `host_layer`
- `repo_lane`
- `host_function`
- `biological_role_metaphor`
- `purpose`
- `non_goals`
- `inputs`
- `outputs`
- `upstream_dependencies`
- `downstream_consumers`
- `authority_class`
- `governed_by`
- `claim_classes_supported`
- `evidence_classes_produced`
- `promotion_relevance`
- `failure_if_removed`
- `main_risks`
- `membrane_contracts`
- `workflow_participation`
- `interface_clarity`
- `evidence_maturity`
- `bounded_influence`
- `removal_impact`
- `notes`

### Minimal example shape

```yaml
subsystem_id: SC-SUBSYSTEM-0001
name: topological-memory-v0
status: infrastructural
host_layer: memory
repo_lane: validation
host_function: continuity retrieval
biological_role_metaphor: memory organelle candidate
purpose: Provide inspectable path-structured retrieval over project memory artifacts.
non_goals:
  - replace all search
  - self-authorize concept promotion
inputs:
  - graph artifacts
  - benchmark queries
  - retrieval prompts
outputs:
  - retrieval paths
  - comparison reports
  - scored recall artifacts
upstream_dependencies:
  - memory artifacts
  - graph schemas
  - retrieval scripts
 downstream_consumers:
  - planning workflows
  - governance review
authority_class: infrastructural
governed_by:
  - validation reports
  - promotion gates
  - schema conformance
claim_classes_supported:
  - C
  - E
evidence_classes_produced:
  - retrieval evidence
  - benchmark comparison evidence
promotion_relevance: supports continuity and admissible recall
failure_if_removed: continuity-aware workflows degrade into flatter retrieval and weaker inspectability
main_risks:
  - enclave risk
  - overfit to benchmark artifacts
membrane_contracts:
  - memory-dispatch-v1
  - memory-governance-v1
workflow_participation: partial
interface_clarity: medium
evidence_maturity: mixed
bounded_influence: explicit
removal_impact: degrades
notes: Candidate near-core organelle if standard workflows adopt outputs.
```

The metaphor is permitted here, but the record itself must remain operational.

### Registry interpretation rule

Avoid a single scalar assimilation score for now.

Until the project has clearer empirical update rules, assimilation should be tracked through explicit dimensions rather than a vibes-bearing number. The fields above are intended to make disagreements inspectable:

- is the host function clear?
- is there standard workflow participation?
- is the influence bounded?
- is the evidence mature enough?
- does removal merely degrade behavior, or actually break a host pathway?

---

## 13. Membrane contracts (v0)

A membrane contract specifies how two host layers interact without collapsing their distinction.

### 13.0 Membrane artifact shape

To become part of the architecture rather than just this document, each membrane should eventually exist as its own artifact.

Suggested location:

- `spine/membranes/<membrane_id>.yaml`

Suggested fields:

- `membrane_id`
- `between_layers`
- `purpose`
- `allowed_flows`
- `forbidden_flows`
- `required_evidence`
- `authority_limits`
- `artifacts_emitted`
- `failure_mode`
- `notes`

Minimal example shape:

```yaml
membrane_id: memory-dispatch-v1
between_layers:
  - memory
  - circulatory
purpose: Allow dispatch to consume inspectable continuity artifacts without granting memory autonomous execution authority.
allowed_flows:
  - context slices
  - retrieval paths
  - continuity summaries
forbidden_flows:
  - autonomous execution triggers from memory alone
  - unreferenced recall artifacts affecting dispatch
required_evidence:
  - inspectable source artifact
  - request provenance
authority_limits:
  - memory may inform dispatch
  - memory may not directly execute runtime actions
artifacts_emitted:
  - dispatch consultation record
failure_mode: memory-oracle creep or amnesia-plumbing
notes: initial membrane for continuity-aware automation
```

### 13.1 Theory ↔ Governance membrane

**Purpose:** prevent doctrine from acting as unbounded authority while still allowing theory to shape admissible structure.

**Contract rules:**
- Theory may define candidate distinctions, invariants, and interpretation frames.
- Governance may only accept theory-backed claims when they are tied to explicit evidence classes.
- No concept may be promoted solely because it is elegant, resonant, or comprehensive.
- Theory can compress evidence; it cannot replace it.

**Failure mode:** cosmology drift; interpretive beauty outranks validation.

### 13.2 Memory ↔ Dispatch membrane

**Purpose:** make continuity operational without forcing dispatch to inherit all memory semantics.

**Contract rules:**
- Dispatch may request context slices, continuity summaries, or retrieval paths.
- Memory outputs must be inspectable and referenceable.
- Dispatch decisions should record whether memory was consulted and what artifact informed action.
- Memory cannot silently trigger execution on its own.

**Failure mode:** either amnesia-plumbing or memory-oracle creep.

### 13.3 Experiment ↔ Governance membrane

**Purpose:** allow exploratory systems to generate pressure without granting them sovereign truth.

**Contract rules:**
- Experimental outputs are evidence candidates, not self-validating conclusions.
- Each experiment must declare what claim class it can support.
- Promotion-relevant use of experiment outputs requires a review path.
- Experimental novelty is never itself sufficient evidence.

**Failure mode:** the host becomes aesthetically driven by its own mutation chamber.

### 13.4 Governance ↔ Runtime membrane

**Purpose:** connect legitimacy to execution without turning governance into a decorative archive.

**Contract rules:**
- Canonical or infrastructural decisions should be able to alter runtime defaults, routes, or availability.
- Runtime events should generate inspectable artifacts that governance can ingest as pressure or evidence.
- Governance records must distinguish descriptive logging from binding control.
- Runtime cannot claim canonical status for outputs that have not passed the relevant governance pathway.

**Failure mode:** governance theater or runtime anarchy.

---

## 14. Revised recommended statuses (v1)

### Temporal predictive processing bridge
- **Recommended status:** advisory
- **Why:** architecturally important interpretive layer, but not yet tightly bound to executable criteria

### Topological memory v0
- **Recommended status:** infrastructural-candidate
- **Why:** already produces inspectable operational artifacts and has a plausible path to near-core host function

### Dispatch hardening
- **Recommended status:** infrastructural
- **Why:** clearly host-critical metabolic flow

### Hyperstition control corridor
- **Recommended status:** experimental
- **Why:** high-value exploratory organ, but should remain bounded until evidence pathways are clearer

### Spine governance v1
- **Recommended status:** canonical-candidate
- **Why:** strongest current claim to regulating host legitimacy, but must still prove runtime consequence

---

## 15. Decision questions that now matter most

To continue architecture convergence, Sandy Chaos should answer the following in explicit form.

### Q1. What is the unit of evolution?
Possible answers:
- concept
- concept cluster
- workflow
- runtime behavior
- artifact bundle

Current best answer:
- **concepts and concept-clusters, with artifact bundles as evidence carriers**

### Q2. What is inherited?
Possible answers:
- documents
- schemas
- ledgers
- retrieval graphs
- runtime defaults
- naming and interface constraints

Current best answer:
- **constraints, artifacts, and legitimacy traces** are what the host most reliably inherits

### Q3. What counts as selection pressure?
Possible answers:
- empirical performance
- retrieval utility
- workflow adoption
- runtime survivability
- governance approval
- explanatory compression

Current best answer:
- selection pressure should be **multi-source**, but governance must define admissibility

### Q4. What makes a subsystem part of the body?
Current best answer:
- stable host function
- membrane contracts
- workflow participation
- governance placement
- non-ornamental consequence

---

## 16. Next actions

### Immediate
1. Create a lightweight subsystem registry with the fields proposed above.
2. Mark each current major subsystem as experimental / advisory / infrastructural / canonical-candidate.
3. Define at least one membrane contract artifact for each missing interface class.
4. Decide whether the host definition in Section 10 is accepted as the current working identity.

### Near-term
1. Decide whether topological memory is required infrastructure for continuity-aware automation.
2. Decide whether spine governance is descriptive or actually authoritative.
3. Define what evidence class experimental corridor outputs belong to.
4. Specify which runtime events should feed back into pressure or promotion state.

### Failure condition for this document
This document fails if it remains purely metaphorical and does not change:
- naming
- subsystem boundaries
- workflow requirements
- interface contracts
- or promotion criteria

If it does not alter actual design decisions, it is only atmospheric language.
