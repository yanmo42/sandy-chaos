# 19 Surface Authority Architecture

> **Status:** Draft v0
>
> **Document role:** canonical design/governance map for Sandy Chaos surface classes, authority layers, and obedience boundaries.
>
> This document is downstream of:
>
> - `FOUNDATIONS.md`
> - `docs/01_foundations.md`
> - `docs/07_agentic_automation_loop.md`
> - `docs/12_yggdrasil_continuity_architecture.md`
> - `docs/17_endosymbiosis_and_host_assimilation.md`
> - `docs/18_adaptive_substrate_and_host_binding.md`
> - `spine/README.md`
>
> It does **not** replace those documents. It defines how major repo surfaces should be classified, how authority should flow, and how metaphor should remain subordinate to inspectable architecture.

---

## 1) Purpose

Sandy Chaos is accumulating multiple kinds of artifacts:

- canonical research docs,
- orchestration and runtime machinery,
- subsystem records and membrane contracts,
- exploratory experiments,
- symbolic maps and worked specimens,
- archival drafts and speculative residues.

Those artifacts do not all have the same authority.
If they are allowed to blur together, the repo becomes harder to reason about, harder to audit, and easier to overclaim from.

This document therefore defines a top-level architecture for four things:

1. **surface class** — what kind of repo object something is,
2. **authority layer** — what kind of obedience or constraint it may exercise,
3. **interface discipline** — what may talk to what and under what conditions,
4. **legitimacy path** — how something becomes more authoritative without silently promoting itself.

---

## 2) Claim discipline for this document

### Defensible now
Sandy Chaos needs a clearer distinction between:

- what is canonical versus exploratory,
- what is symbolic versus operational,
- what is preserved for lineage versus obeyed in the present,
- and what may constrain downstream behavior versus what may only suggest candidate directions.

### Plausible but unproven
A compact layered vocabulary using **soul / heart / brain / hand / fingers** can help preserve legibility, provided those terms are treated as architectural mnemonics rather than metaphysical claims.

### Speculative
A future machine-readable implementation could allow repo surfaces, automation pathways, and promotion rules to be checked automatically against these layer and authority constraints.

---

## 3) Non-goals

This document does **not**:

- replace `FOUNDATIONS.md` as the hard constraint surface,
- prove theoretical claims,
- grant canonical status by description alone,
- license symbolic language to do causal or governance work,
- or merge identity, governance, planning, and execution into one undifferentiated voice.

---

## 4) Core principle

**Presence is not authority.**

A file does not become canonical because it exists.
A branch does not become legitimate because it merged.
A symbolic construction does not become operative because it is elegant.
An experimental output does not become policy because it is suggestive.

For a surface to gain authority, it must have:

- a declared role,
- a declared legitimacy source,
- bounded interfaces,
- an inspectable promotion path,
- and evidence proportionate to consequence.

---

## 5) Compact architecture map

The top-level stack is:

```text
SOUL  -> charter, enduring aim, identity boundary
HEART -> legitimacy, governance, promotion discipline
BRAIN -> planning, synthesis, interpretation, experiment design
HAND  -> orchestration, routing, dispatch, coordination
FINGERS -> local effectors, simulations, validators, adapters, probes
```

The basic rule is:

- **authority flows downward**,
- **evidence flows upward**,
- **interfaces flow laterally only through declared membranes**,
- **no layer self-legitimates**.

This can be expressed more explicitly:

```text
soul authorizes heart
heart constrains brain
brain instructs hand
hand invokes fingers
fingers emit evidence upward
```

### Interpretation rule

These names are an architectural shorthand only.
They are useful insofar as they preserve distinctions among:

- identity,
- governance,
- planning,
- coordination,
- and local action.

They should not be read as proof of hidden ontology.

---

## 6) Role and authority stack

### 6.1 Soul

**Function:** charter, identity boundary, enduring aim.

**What it answers:**
- what the project is trying to be,
- what hard boundaries it refuses to violate,
- what it is for.

**Authority:** highest, but narrow.

**May:**
- define durable purpose,
- define non-negotiable boundaries,
- define the kind of system Sandy Chaos is trying to remain.

**May not:**
- directly rewrite runtime behavior,
- substitute for evidence,
- or self-certify lower-layer claims as true.

**Typical surfaces:**
- `FOUNDATIONS.md`
- selected blueprint or charter-level docs

### 6.2 Heart

**Function:** legitimacy, governance, promotion, admission, bounded obedience.

**What it answers:**
- what counts,
- what may be promoted,
- what remains advisory,
- what is allowed to affect standard host behavior.

**Authority:** normative over canon and policy-bearing pathways.

**May:**
- define promotion gates,
- define subsystem status,
- define membrane requirements,
- classify evidence-bearing surfaces.

**May not:**
- invent evidence,
- silently override declared interfaces,
- or treat aspiration as validation.

**Typical surfaces:**
- `spine/*`
- subsystem registry records
- membrane contracts
- promotion ledgers

### 6.3 Brain

**Function:** interpretation, synthesis, planning, design of tests and candidate actions.

**What it answers:**
- what might be true,
- what should be tested next,
- how surfaces relate,
- what plan best fits the current constraints.

**Authority:** advisory and executive-proposal authority, not legitimacy authority.

**May:**
- produce plans,
- propose experiments,
- compress theory,
- map evidence into candidate next moves.

**May not:**
- promote itself to canonical status,
- bypass governance,
- or treat symbolic artifacts as proof.

**Typical surfaces:**
- synthesis docs
- planning artifacts
- bridge notes
- experiment-design docs

### 6.4 Hand

**Function:** coordination, routing, dispatch, scheduling, execution control.

**What it answers:**
- what runs,
- when it runs,
- through which interface,
- under what guardrails.

**Authority:** operational only.

**May:**
- invoke tools,
- dispatch workflows,
- collect outputs,
- enforce local execution guardrails.

**May not:**
- decide legitimacy,
- redefine project aim,
- or smuggle policy changes in as implementation details.

**Typical surfaces:**
- orchestrators
- schedulers
- runtime config and dispatch machinery

### 6.5 Fingers

**Function:** bounded local action.

**What it answers:**
- what a specific tool, sim, validator, or adapter does.

**Authority:** minimal and task-bound.

**May:**
- simulate,
- validate,
- transform,
- benchmark,
- emit measurements and artifacts.

**May not:**
- set project policy,
- act as global planner,
- or alter canonical state without an upstream pathway.

**Typical surfaces:**
- scripts
- local models
- validators
- probes
- adapters
- tests

---

## 7) Surface classes

This document defines four top-level surface classes.

### 7.1 Canon

**Definition:** a surface with standing relevance to present repository interpretation, constraints, or standard workflows.

**Use:** what the system may presently obey, cite, or depend on through approved pathways.

**Examples:**
- numbered canonical docs,
- validated governance artifacts,
- subsystem records with standing authority,
- stable runtime contracts.

**Requirements:**
- declared role,
- explicit compatibility with Foundations,
- bounded interfaces,
- visible claim-tier discipline.

### 7.2 Experimental

**Definition:** a surface that generates candidate evidence, candidate mechanisms, or candidate procedures without standing canonical effect.

**Use:** active exploration.

**Examples:**
- exploratory simulations,
- probes,
- new subsystem trials,
- research prototypes.

**Rule:** experimental outputs may pressure canon, but may not silently become canon.

### 7.3 Symbolic specimen

**Definition:** a worked symbolic artifact used to inspect, compress, or communicate structure without carrying default governance or runtime authority.

**Use:** legibility, examples, conceptual stress tests, form-preserving illustration.

**Examples:**
- symbolic maps,
- worked operator examples,
- stylized structural specimens.

**Rule:** symbolic specimens may clarify architecture, but they do not authorize it.

### 7.4 Speculative archive

**Definition:** preserved material with lineage or retrieval value but without standing present authority.

**Use:** memory, archaeology, recovery of prior reasoning, comparison against current doctrine.

**Examples:**
- `docs/archive/*`
- superseded theory notes,
- historical speculative drafts.

**Rule:** archival value is not present legitimacy.

---

## 8) Surface class versus authority

Surface class and authority are separate.

A useful distinction is:

- **surface class** says what kind of thing an artifact is,
- **authority class** says what it is allowed to affect.

Recommended authority classes for governed repo artifacts are:

- `experimental`
- `advisory`
- `infrastructural`
- `canonical-candidate`
- `canonical`

These follow the subsystem-governance vocabulary already present in Sandy Chaos.
Surfaces that are merely illustrative or archival may omit `authority_class` entirely rather than inventing a second parallel enum.

### Practical reading

- A prompt packet is usually **experimental** or **advisory**.
- A runtime support layer may be **infrastructural**.
- A subsystem under serious review may be **canonical-candidate**.
- A governance-bearing membrane or standing registry artifact may be **canonical**.
- A symbolic specimen or speculative archive may simply omit `authority_class` because it is not a governed control surface.

This distinction matters because not every visible artifact should govern behavior in the same way.

---

## 9) Interface and obedience rules

### 9.1 Allowed authority direction

The default obedience stack is:

- soul -> heart
- heart -> brain
- brain -> hand
- hand -> fingers

### 9.2 Allowed evidence direction

The default evidence stack is:

- fingers -> hand
- hand -> brain
- brain -> heart
- heart -> soul only as interpreted governance state, not raw proof

### 9.3 Lateral interaction rule

Lateral communication is allowed only through declared interfaces or membranes.

Examples:
- theory to governance,
- memory to dispatch,
- experiment to governance,
- governance to runtime.

If a cross-layer dependency matters enough to affect behavior, it should eventually become a named membrane artifact.

### 9.4 Forbidden bypasses

The following should be treated as architectural violations:

- experiment -> runtime policy without governance mediation,
- symbolic specimen -> canonical doctrine without explicit promotion,
- runtime behavior -> self-legitimation as policy,
- archive -> current authority by mere citation,
- planning layer -> unilateral legitimacy assignment,
- identity language -> direct substitution for evidence.

---

## 10) Legitimacy, dependency, and aim

To keep repo growth legible, each major surface should answer five questions.

### 10.1 Aim
What is this surface for?

### 10.2 Legitimacy source
What gives it standing?

Examples:
- Foundations compatibility,
- spine governance placement,
- validation results,
- archival preservation only.

### 10.3 Dependency shape
What does it depend on, and who depends on it?

### 10.4 Interface boundary
What may enter or leave this surface?

### 10.5 Promotion path
How could it become more authoritative, if at all?

If these questions cannot be answered, the surface may still be useful, but it should not be treated as load-bearing.

---

## 11) Naming and classification scheme for repo surfaces

For major docs, subsystems, and operational artifacts, the following metadata is recommended:

```yaml
surface_class: canon | experimental | symbolic-specimen | speculative-archive
authority_class: experimental | advisory | infrastructural | canonical-candidate | canonical
layer: soul | heart | brain | hand | finger
legitimacy_source: foundations | spine | validation | archive
promotion_path: none | experiment-to-canon | specimen-to-concept | archive-only
```

Additional helpful fields:

```yaml
primary_interfaces: []
upstream_dependencies: []
downstream_consumers: []
claim_tier_max: defensible | plausible | speculative
control_effect: none | indirect | direct-approved
```

### Repo-level default interpretation

- `docs/[00-99]_*.md`
  - default: canon-candidate
  - requires explicit role before being treated as canonical authority

- `spine/**`
  - default: heart layer
  - governance-bearing unless explicitly marked otherwise

- `research/**` and exploratory probes
  - default: experimental

- `plans/prompts/**`
  - default: experimental
  - normal authority class: advisory
  - use these to translate canon into bounded implementation pressure, not to define canon directly

- `docs/symbolic-maps/**` or specimen directories
  - default: symbolic-specimen

- `docs/archive/**` and superseded historical materials
  - default: speculative-archive

These defaults should remain overridable, but not ambiguous.

---

## 12) Worked examples

### 12.1 `FOUNDATIONS.md`

- surface class: canon
- authority class: canonical
- layer: soul
- legitimacy source: foundational charter and hard project constraints
- promotion path: none except explicit revision

Reason: this is a hard-boundary surface, not a freeform theory note.

### 12.2 `spine/membranes/governance-runtime-v1.yaml`

- surface class: canon
- authority class: canonical
- layer: heart
- legitimacy source: spine governance and declared runtime membrane role
- promotion path: versioned governance refinement

Reason: it does not prove theory, but it does constrain how governance may affect runtime.

### 12.3 Topological memory subsystem record

- surface class: canon
- authority class: infrastructural
- layer: heart-facing description of a memory-layer subsystem
- legitimacy source: subsystem registry + validation pathway
- promotion path: stronger host adoption and evidence maturity

Reason: it is not a charter surface, but it can become load-bearing infrastructure.

### 12.4 Symbolic map example

- surface class: symbolic-specimen
- authority class: usually omitted; at most advisory if attached to a bounded governed workflow
- layer: usually brain-facing interpretive support
- legitimacy source: explanatory usefulness only
- promotion path: must first become a concept or testable interface claim

Reason: it may illuminate structure without earning control authority.

### 12.5 Archived long-form speculative note

- surface class: speculative-archive
- authority class: omitted
- layer: none in the active obedience stack
- legitimacy source: preservation only
- promotion path: must be re-imported through fresh pressure, not nostalgia

Reason: historical interest is not present governance.

---

## 13) Failure modes if layers blur

### 13.1 Merge-equals-canon confusion
A merged branch is treated as legitimate architecture by default.

**Result:** accidental doctrine.

### 13.2 Experiment-equals-policy confusion
A probe or corridor result begins steering planning or runtime directly.

**Result:** unearned authority.

### 13.3 Symbol-equals-mechanism confusion
A symbolic specimen is read as if it were a validated causal model.

**Result:** metaphor inflation.

### 13.4 Planner-equals-governor confusion
Interpretive intelligence starts deciding legitimacy instead of proposing to governance.

**Result:** cleverness outruns discipline.

### 13.5 Runtime-equals-governance confusion
Operational machinery changes effective policy without emitting governance artifacts.

**Result:** hidden rulemaking.

### 13.6 Archive-equals-authority confusion
Older material is cited as if preservation alone grants current standing.

**Result:** stale doctrine and lineage laundering.

### 13.7 Identity-equals-proof confusion
Project desire, aesthetic coherence, or identity language substitutes for evidence.

**Result:** self-sealing architecture.

### 13.8 Voice collapse
Instinct, coordination, planning, governance, identity, and desire are all expressed through one undifferentiated surface.

**Result:** no legible obedience path, no bounded disagreement, and no reliable audit trail.

---

## 14) Minimal operating rules

1. **Every major surface should declare its class.**
2. **Every load-bearing surface should declare its authority class.**
3. **Experimental outputs do not gain canonical force without promotion.**
4. **Symbolic artifacts do not gain operational force without translation into testable or governed form.**
5. **Archives preserve lineage but do not govern the present.**
6. **Cross-layer influence should pass through named membranes once it becomes recurrent or consequential.**
7. **No layer may authenticate itself as more authoritative than its declared legitimacy source permits.**

---

## 15) Near-term implications for Sandy Chaos

### Defensible now
The repo already contains enough differentiated structure that a top-level surface authority map is useful and likely overdue.

### Plausible but unproven
Adding explicit metadata to major docs, subsystem records, and symbolic surfaces would reduce future ambiguity about what the project is actually allowed to obey.

### Speculative
A future validator could lint for authority violations, such as experimental artifacts being cited in normative contexts without mediation.

---

## 16) Recommended next implementation hooks

If this document proves useful, the next practical moves are:

1. add `surface_class` and `authority_class` to major subsystem and membrane records,
2. mark symbolic-map examples explicitly as `symbolic-specimen`,
3. mark archive surfaces explicitly as non-authoritative,
4. add a light validator that flags obvious authority-bypass patterns,
5. update the docs index to distinguish canonical, experimental, symbolic, and archival reading paths.

---

## 17) Failure condition for this document

This document fails if it remains decorative.

Concretely, it would have failed if after adoption:

- important repo surfaces still cannot be classified,
- authority still defaults to proximity or elegance,
- symbolic materials still drift into policy without translation,
- or runtime and governance still blur together without inspectable membranes.

If that happens, the right response is not to expand this document rhetorically, but to either simplify it or instantiate it more concretely in repo metadata and tooling.
