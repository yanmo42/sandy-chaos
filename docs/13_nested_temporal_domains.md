# 13 Nested Temporal Domains

> **Status:** canonical synthesis / architecture note for multiscale coupling.
>
> This document introduces **Nested Temporal Domains** as a causality-safe architecture for relating fast, meso, and slow processes inside Sandy Chaos. It does **not** replace the project's causal boundary, transport layer, observer-coupling layer, or continuity layer. It sits across them and proposes a clean rule for how temporally distinct domains may exchange usable information without collapsing into hand-waving.
>
> Related docs:
>
> - `docs/01_foundations.md`
> - `docs/02_tempo_tracer_protocol.md`
> - `docs/03_micro_observer_agency.md`
> - `docs/04_neuro_roadmap.md`
> - `docs/05_hyperstition_temporal_bridge_analysis.md`
> - `docs/12_yggdrasil_continuity_architecture.md`
> - `docs/14_cognitive_tempo_orchestration.md`
> - `docs/15_gravitational_centers_and_energistics.md`
>
> Claim posture:
>
> - **Defensible now:** Sandy Chaos already uses multi-timescale framing, bounded-now discipline, read-write observer coupling, and fast/meso/slow cadences. Making the layer relations explicit improves conceptual hygiene.
> - **Plausible but unproven:** modeling these relations as neighbor-layer encodings will improve explanation quality and eventually support cleaner experiments.
> - **Speculative:** Nested Temporal Domains may become a deeper unifying architecture across physics, cognition, narrative, and continuity. That stronger reading should not do mechanism-level work unless benchmarked.

---

## 1) Why this doc exists

Sandy Chaos already has several pieces that imply multiscale structure:

- timing asymmetry over proper-time offset,
- read-write observer coupling,
- fast / meso / slow control loops,
- hyperstitional or narrative boundary variables,
- branching work that runs at different cadences.

What has been missing is a compact rule for how those layers should relate.

Without that rule, multi-timescale language risks becoming loose. With too little structure, every layer can be imagined as talking directly to every other layer, and the framework becomes harder to falsify.

This document proposes a stricter alternative:

> **Nested Temporal Domains** are temporally banded domains that exchange only constrained, neighbor-layer representations under explicit latency, distortion, and reconstruction limits.

That keeps the project's multiscale language useful without granting magical cross-layer access.

---

## 2) Plain-language definition

A **Nested Temporal Domain** is a domain indexed by:

1. a **role polarity** (for example observer/observed, chaser/chased, parent/child), and
2. a **temporal band** (for example fast, meso, slow).

Each domain may communicate in two distinct ways:

- **across polarity** to its opposite-side counterpart at the same temporal band,
- **across tempo** to an adjacent same-role domain at a neighboring temporal band.

This creates a grid-like architecture rather than a flat stack or a one-way hierarchy.

Example schematic:

```text
slow observer   <---->   slow observed
      ^                          ^
      |                          |
      v                          v
meso observer   <---->   meso observed
      ^                          ^
      |                          |
      v                          v
fast observer   <---->   fast observed
```

The key restriction is that these links are **neighbor-first**.

---

## 3) Core primitives

### 3.1 Domain index

Write a domain as:

$$
D_{r,k}
$$

where:

- $r$ is the role polarity index,
- $k$ is the temporal-band index.

A minimal local chart may be written as:

$$
D_{r,k} = (x_{r,k}, y_{r,k}, \pi_{r,k}, \delta_{r,k})
$$

where:

- $x_{r,k}$ = local state,
- $y_{r,k}$ = locally available observables,
- $\pi_{r,k}$ = policy / interpretation / coupling state,
- $\delta_{r,k}$ = latency budget or temporal contact quality.

### 3.2 Role polarity

Role polarity names the relational side of a domain.

Useful Sandy Chaos examples:

- **observer / observed**
- **chaser / chased**
- **parent / child**
- **planner / builder** or **builder / verifier** when using operational role views

These are not identical roles, but they can be modeled with the same architectural grammar.

### 3.3 Temporal band

Temporal band names the update cadence of the domain.

The current project already uses a natural triplet:

- **fast** — rapid local selection / correction,
- **meso** — routing / alignment / summary,
- **slow** — continuity / goals / policy burden.

These bands map directly onto Yggdrasil's cadence surfaces (see `docs/12_yggdrasil_continuity_architecture.md` §5 Rule 5): **fast = edge**, **meso = bridge**, **slow = spine**. Temporal-band updates should therefore respect the same forward-causal promotion discipline — edge observations inform bridge summaries, and bridge summaries may justify spine revisions, but raw fast-band activity should not rewrite slow-band state directly.

More bands are possible, but the architecture should stay sparse unless measurement justifies finer resolution.

### 3.4 Adjacency

Adjacency is load-bearing.

By default:

- a domain may couple to its opposite-role counterpart at the **same** temporal band,
- a domain may couple to the **same role** at an **adjacent** temporal band,
- direct long-jump or all-to-all coupling is **not** assumed.

This rule prevents unconstrained omniscience.

---

## 4) Allowed coupling types

### 4.1 Polarity coupling

Across-role, same-band transfer:

$$
E_{pol}: D_{r,k} \rightarrow D_{\bar{r},k}
$$

Interpretation:

- observer ↔ observed,
- chaser ↔ chased,
- parent ↔ child.

This captures the idea that opposing sides mutually constrain one another.

### 4.2 Temporal coupling

Same-role, adjacent-band transfer:

$$
E_{tmp}: D_{r,k} \rightarrow D_{r,k\pm1}
$$

Interpretation:

- fast observer ↔ meso observer,
- meso observer ↔ slow observer,
- fast chased ↔ meso chased,
- branch output ↔ meso summary ↔ spine-level continuity note.

### 4.3 Diagonal coupling

Direct diagonal coupling should be **disallowed by default**.

If a slow observer affects a fast observed domain, that interaction should usually be represented as a composition of admissible neighbor links:

$$
D_{observer,slow} \rightarrow D_{observer,meso} \rightarrow D_{observed,meso} \rightarrow D_{observed,fast}
$$

That may be inefficient, but it is conceptually honest.

---

## 5) Neighbor-layer codec

The central mechanism is not raw messaging. It is a **neighbor-layer codec**.

Each admissible transfer should be described using four operations:

1. **Embed** — write a constrained representation of local state into a neighbor layer.
2. **Extract** — recover a usable representation from the neighbor-layer signal.
3. **Translate** — convert that representation into local variables or control terms.
4. **Reconstruct** — form a bounded local model of the neighboring domain.

A minimal transfer object might look like:

```text
TransferBundle {
  payload,
  source_domain,
  target_domain,
  latency,
  distortion,
  confidence,
  provenance,
  validity_window
}
```

### Rule: no raw cross-domain state access

This is the hard rule of the architecture.

Domains do **not** get unrestricted access to one another's full state.
They exchange:

- compressed summaries,
- bounded control signals,
- gradient-like hints,
- partial observations,
- or policy-relevant aggregates.

This aligns naturally with:

- bounded-now access,
- causal-admissible retrodiction,
- partial observability,
- and information-bottleneck style coarse-graining.

---

## 6) Relationship to existing Sandy Chaos layers

### 6.1 Foundations (`01`)

Nested Temporal Domains inherit the non-negotiable causal boundary:

- no retrocausal channel,
- no global-now oracle,
- no future state determining present state.

Any transfer must still reduce to forward dynamics plus lawful inference.

### 6.2 Tempo Tracing (`02`)

Tempo Tracing remains the metrology layer.
It measures directional asymmetry and timing structure over $\Delta\tau$.

Nested Temporal Domains do not replace those metrics; they provide a way to say **which layers** are exchanging constrained representations and at what cadence.

### 6.3 Micro-Observer & Agency (`03`)

Read-write observer coupling is one concrete instance of polarity coupling.

An observer extracts information from an observed domain and also perturbs future admissible dynamics. When this occurs across fast/meso/slow bands, the resulting architecture is naturally described as a stack of nested temporal domains with bounded neighbor-layer exchange.

### 6.4 Neuro Roadmap (`04`)

The fast / meso / slow loops already named there can be treated as temporal bands, mapping explicitly onto the **edge / bridge / spine** cadences.

Nested Temporal Domains sharpen that framing by making two rules explicit:

1. not every band talks directly to every other band,
2. what passes between bands is a transformed representation, not full state.

### 6.5 Hyperstition Temporal Bridge (`05`)

The hyperstition note models time as an observer-indexed ordering of irreversible constraint updates.

Nested Temporal Domains provide a cleaner architectural story for how those updates may propagate across multiple cadences without turning narrative or symbolic language into an unconstrained force.

### 6.6 Yggdrasil Continuity (`12`)

Yggdrasil is the continuity architecture for branching work.

Nested Temporal Domains can be read as a **cross-cutting coupling grammar** that helps explain why fast / meso / slow continuity surfaces exist at all. But the two documents operate at different levels:

- **Yggdrasil** governs continuity, promotion, and provenance,
- **Nested Temporal Domains** govern admissible multiscale coupling language.

For the cross-cutting thesis built on top of this grammar, see:

- **[15 Gravitational Centers and Energistics](15_gravitational_centers_and_energistics.md)**

---

## 7) Useful instantiations

### 7.1 Observer / observed

Best when discussing:

- measurement,
- read-write coupling,
- bounded-now estimation,
- reconstruction from traces.

### 7.2 Chaser / chased

Best when discussing:

- delayed pursuit,
- stale state models,
- cadence inversion,
- topology reshaping,
- prediction failure under latency.

This is the most operational polarity for pursuit-evasion and tempo-chase style work.

### 7.3 Parent / child

Best when discussing:

- containment and recursion,
- branch / spine relations,
- governance and promotion burden,
- continuity across consequence levels.

No single polarity should monopolize the architecture.
The umbrella concept should remain more general than any one metaphor.

---

## 8) Failure conditions

The architecture is failing if:

1. **all-to-all coupling sneaks back in**
   - every layer can directly access every other layer without declared mediation.

2. **loss models disappear**
   - transfers do not specify what is preserved, compressed, distorted, or dropped.

3. **latency is ignored**
   - domains are treated as if they share a frictionless present.

4. **metaphor substitutes for mechanism**
   - role language does explanatory work without state/measurement/operator grounding.

5. **reconstruction is overstated**
   - extraction is allowed to recover hidden full state with no uncertainty burden.

6. **speculative ontology leaks into policy**
   - the architecture is used to justify strong claims without tests, nulls, or governance gates.

---

## 9) Near-term implementation hooks

Near-term, the architecture should change explanation and benchmarking before it changes ontology.

Useful next steps:

1. **Tag fast / meso / slow components explicitly** in theory notes and simulations where helpful.
2. **Define a minimal neighbor-transfer schema** for multiscale summaries, latency, and distortion.
3. **Benchmark neighbor-only vs unrestricted transfer assumptions** in toy systems.
4. **Test reconstruction quality under controlled loss** rather than assuming clean cross-layer decode.
5. **Use the architecture as a doc-level hygiene tool first** before promoting it into hard policy.

A good initial experiment family would compare:

- neighbor-only coupling,
- direct all-to-all coupling,
- and no cross-band coupling,

under the same task, noise, and latency budget.

---

## 10) Summary

Nested Temporal Domains give Sandy Chaos a disciplined way to talk about multiscale interaction.

The core commitments are simple:

- domains are indexed by role and temporal band,
- coupling is neighbor-first,
- transfer is encoded rather than raw,
- latency and distortion must be declared,
- and the causal boundary remains untouched.

If this architecture proves useful, it can unify several existing Sandy Chaos threads without flattening them into mysticism.
If it fails, it should fail cleanly by showing that the extra structure adds no explanatory or experimental value.

For the bridge document that instantiates this coupling grammar as a predictive-processing architecture under explicit transfer constraints, see:

- **[16 Temporal Predictive Processing via Potential-Flow Contracts](16_temporal_predictive_processing.md)**
