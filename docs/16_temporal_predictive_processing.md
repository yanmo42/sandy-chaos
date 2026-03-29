# 16 Temporal Predictive Processing via Potential-Flow Contracts

> **Status:** canonical synthesis / formal draft bridge document.
>
> This document specifies a candidate bridge architecture between **Nested Temporal Domains** and **Potential-Flow Contracts**: predictive processing across temporal frames using graph-constrained message passing, with admissible transfers regulated by explicit contract structure.
>
> Here, “time-index-agnostic latent space” means a **shared latent coordinate manifold used to align states from multiple temporal frames without claiming that time is unreal or optional**.
>
> Related docs:
>
> - `docs/02_tempo_tracer_protocol.md`
> - `docs/03_micro_observer_agency.md`
> - `docs/04_neuro_roadmap.md`
> - `docs/11_geodesic_hydrology_contracts.md`
> - `docs/13_nested_temporal_domains.md`
> - `docs/14_cognitive_tempo_orchestration.md`
> - `docs/prediction-protocol.md`
> - `docs/assumptions_register.md`
> - `docs/theory-implementation-matrix.md`
>
> Claim posture:
>
> - **Defensible now:** multiscale predictive architectures can be expressed as bounded cross-frame message passing between adjacent temporal domains, with explicit latency, distortion, and admissibility accounting.
> - **Plausible but unproven:** graph-neural operators constrained by potential-flow contracts may improve temporal coherence, stability, and interpretability relative to unconstrained coupling.
> - **Speculative:** this architecture may capture a deeper general principle of intelligence or physical cognition beyond the benchmarked task families where it is tested.

---

## 1) Why this doc exists

Sandy Chaos already has two strong pieces that almost touch but do not yet cleanly join.

`13_nested_temporal_domains.md` gives the project a **multiscale coupling grammar**:

- neighbor-first transfer,
- bounded representations rather than raw omniscient state access,
- explicit latency, distortion, and reconstruction burden.

`11_geodesic_hydrology_contracts.md` gives the project a **transport-and-constraint grammar**:

- potential/head fields,
- admissible descent structure,
- path-functional evaluation,
- and hard discipline against metaphor pretending to be mechanism.

What has been missing is a single place to state how these two grammars can combine into a predictive architecture.

This document is that bridge.

The goal is not to introduce a new metaphysical layer.
The goal is to provide a testable, causality-safe model class for predictive processing across temporal frames.

---

## 2) Thesis in one sentence

> **Predictive processing across temporal frames can be modeled as graph-constrained message passing between adjacent temporal domains, where admissible transfers are regulated by potential-flow contracts over a shared latent coordinate space.**

This is the intended strong form.

The intended weak form is just as important:

- the graph is bounded,
- the transfers are constrained,
- the latent space is a modeling device,
- and the claim succeeds only if it produces measurable lift over simpler baselines.

---

## 3) Core terms

### 3.1 Temporal frame

A **temporal frame** is a process band or update cadence such as:

- `fast`
- `meso`
- `slow`

More refined frame indices are allowed, but the default architecture remains sparse unless finer structure is empirically justified.

### 3.2 Predictive processing

**Predictive processing** here means that each frame maintains and updates a local predictive state:

- what it expects,
- what error it currently carries,
- how much uncertainty remains unresolved,
- and how it revises that state under incoming evidence and neighbor-frame transfer.

This document does **not** require commitment to any single grand predictive-processing ontology.
It uses the term in an operational sense.

### 3.3 Time-index-agnostic latent coordinate space

A **time-index-agnostic latent coordinate space** is a shared latent manifold used to align states from distinct frames.

It is called “time-index-agnostic” because:

- it is not tied to one specific update cadence,
- it can host comparable embeddings from multiple frames,
- and it allows cross-frame transfer without forcing all processing into one clock.

It is **not** a claim that time is illusory or absent.
It is a coordinate convenience for multiscale alignment.

### 3.4 Potential-flow contract

A **potential-flow contract** is a transfer rule that constrains what counts as admissible movement or message passage across an edge in the multiframe graph.

It defines:

- what gradients or compatibility pressures matter,
- what movement budget is allowed,
- what distortion or latency burden must be recorded,
- and when a proposed transfer is invalid.

### 3.5 Neighbor-first coupling

This document inherits the hard rule from `13_nested_temporal_domains.md`:

> **No raw cross-domain state access.**

Domains exchange constrained representations with explicit:

- source,
- target,
- latency,
- distortion,
- confidence,
- provenance,
- and reconstruction limits.

---

## 4) Architecture at a glance

The architecture has five layers:

1. **Local frame state**
   - each temporal frame maintains its own predictive state.

2. **Cross-frame graph**
   - only declared edges may exchange signals.

3. **Shared latent coordinate space**
   - local states are encoded into a common representation family.

4. **Potential-flow contracts**
   - cross-frame transfers must satisfy explicit admissibility constraints.

5. **Prediction-and-coherence objective**
   - performance is scored by predictive quality, bounded violations, and robustness under perturbation.

This is the minimum structure needed to make the idea operational rather than merely evocative.

---

## 5) State model

Let temporal frames be indexed by `k`, with a default set such as:

- `k ∈ {fast, meso, slow}`

Let role polarity optionally be indexed by `r` when needed, as in `13_nested_temporal_domains.md`.

A local frame state may be written as:

$$
S_{r,k}(t) = \big(x_{r,k}(t),\; b_{r,k}(t),\; e_{r,k}(t),\; z_{r,k}(t)\big)
$$

where:

- $x_{r,k}(t)$ = local observable or system state,
- $b_{r,k}(t)$ = predictive belief state,
- $e_{r,k}(t)$ = local prediction error / uncertainty burden,
- $z_{r,k}(t)$ = latent embedding in a shared coordinate space $Z$.

The multiframe coupling graph is:

$$
G = (V,E)
$$

where each vertex is a frame or frame-subsystem, and each edge declares an allowed transfer corridor.

By default, admissible edges are:

- same-role, adjacent-tempo edges,
- opposite-role, same-band edges,
- and no diagonal or long-jump edges unless explicitly justified.

This keeps the architecture aligned with the neighbor-first doctrine.

---

## 6) Potential-flow contract semantics

For each admissible edge $(i,j)$ in the graph, define a contract:

$$
C_{ij} = (\Phi_{ij}, B_{ij}, \tau_{ij}, \delta_{ij}, \varepsilon_{ij})
$$

where:

- $\Phi_{ij}(z_i, z_j)$ = a compatibility or potential function over latent states,
- $B_{ij}$ = a movement / flow budget,
- $\tau_{ij}$ = latency budget or delay accounting term,
- $\delta_{ij}$ = distortion or loss accounting term,
- $\varepsilon_{ij}$ = admissibility threshold.

### 6.1 What the contract actually constrains

The contract does **not** magically explain transfer.
It constrains it.

At minimum, a contract should regulate some combination of:

- latent transition magnitude,
- message norm or information budget,
- continuity of transfer across successive updates,
- allowable distortion under compression,
- and directional asymmetry under latency.

### 6.2 Residual rule

A proposed transfer on edge $(i,j)$ is admissible only if its residual remains below threshold:

$$
r_{ij} \le \varepsilon_{ij}
$$

where $r_{ij}$ is a contract-specific error or violation quantity.

This residual is load-bearing.
If the architecture cannot define it, log it, and test it, then the contract layer is decorative rather than operational.

### 6.3 Why potential-flow language belongs here

The relevant inheritance from `11_geodesic_hydrology_contracts.md` is:

- there is a structured notion of descent or compatibility pressure,
- movement is constrained by geometry and budget,
- and trajectories matter, not just terminal guesses.

In this document, that logic is applied to **cross-frame predictive transfer**.

---

## 7) Graph-neural operator layer

A graph-neural operator provides the computational mechanism.

A minimal update cycle is:

1. **Encode local state into latent coordinates**

$$
z_i = \mathrm{Enc}_\theta(x_i, b_i, e_i)
$$

2. **Propose cross-frame messages for each admissible edge**

$$
m_{ij} = \mathrm{Msg}_\theta(z_i, z_j)
$$

3. **Project each proposal into the contract-feasible set**

$$
m^*_{ij} = \mathrm{Proj}_{C_{ij}}(m_{ij})
$$

4. **Aggregate admissible messages and update the target frame**

$$
z'_j = \mathrm{Upd}_\theta\left(z_j, \sum_i m^*_{ij}\right)
$$

5. **Update predictive belief state and local error terms**

$$
b'_j, e'_j = \mathrm{BeliefUpdate}(z'_j, x_j)
$$

This is the clearest current computational reading of the proposal.

### 7.1 Why graph-neural structure is a fit

Graph-neural structure is appropriate here because:

- the coupling topology is sparse and explicit,
- transfer is edge-conditioned,
- local neighborhoods matter,
- and all-to-all coupling should be discouraged by default.

This makes the graph layer a natural mechanism for enforcing the architecture rather than just decorating it.

---

## 8) Objective and loss structure

A minimal objective should include four terms:

1. **Prediction loss**
   - local and cross-frame forecasting error.

2. **Contract violation penalty**
   - penalty for transfers that exceed admissibility thresholds.

3. **Latency / distortion penalty**
   - cost for stale or overly lossy transfer.

4. **Cross-frame coherence term**
   - reward for useful alignment across temporal bands when such alignment improves task performance.

A schematic objective:

$$
\mathcal{L} = \mathcal{L}_{pred} + \lambda_c \mathcal{L}_{contract} + \lambda_\tau \mathcal{L}_{latency} + \lambda_h \mathcal{L}_{coherence}
$$

This is sufficient for an implementation-facing reading.
More elaborate free-energy or path-functional terms may be added later if they produce actual comparative lift.

---

## 9) Relationship to existing Sandy Chaos docs

### 9.1 Nested Temporal Domains (`13`)

`13_nested_temporal_domains.md` provides the **coupling grammar**.

This document inherits from `13`:

- neighbor-first transfer,
- bounded representation exchange,
- explicit latency/distortion burden,
- and rejection of raw omniscient cross-layer state access.

So:

- **Nested Temporal Domains** tells us **how the multiscale lanes may connect**,
- **this document** gives one candidate predictive-processing implementation of that grammar.

### 9.2 Potential-Flow Contracts (`11`)

`11_geodesic_hydrology_contracts.md` provides the **transport-and-constraint logic**.

This document inherits from `11`:

- potential/head structure,
- admissible transport under declared constraints,
- path sensitivity,
- and the rule that metaphor must cash out in operator/state terms.

So:

- **Potential-Flow Contracts** tells us **how admissibility and transport pressure may be described**,
- **this document** applies that logic to cross-frame predictive transfer.

### 9.3 Micro-Observer & Agency (`03`)

`03_micro_observer_agency.md` remains the observer-coupling and intervention discipline layer.

This document does not override it.
Instead, it gives one concrete way to model multiframe predictive revision under bounded coupling.

### 9.4 Tempo Tracer Protocol (`02`)

`02_tempo_tracer_protocol.md` remains the measurement and directional-asymmetry layer.

This document should be treated as compatible with `02` only if the resulting architecture produces measurable timing- and asymmetry-relevant observables rather than just cleaner prose.

### 9.5 Neuro Roadmap (`04`)

`04_neuro_roadmap.md` already points toward multi-cadence neurological organization.

This document sharpens one specific computational hypothesis:

- predictive processing may be distributed across temporal frames,
- with cross-frame transfer mediated by bounded graph structure,
- and constrained by admissibility contracts rather than unconstrained latent blending.

---

## 10) Failure conditions

This proposal should be treated as failing if any of the following occur.

### 10.1 All-to-all coupling quietly returns

If every frame effectively accesses every other frame directly, the architecture has lost its main discipline.

### 10.2 “Atemporal” language does ontological work

If the latent coordinate space is used to imply that time is unreal, secondary, or bypassed as a hard physical constraint, the proposal has drifted out of bounds.

### 10.3 Contract residuals are decorative

If the contract layer cannot define measurable violation quantities, or those quantities never affect training, inference, or analysis, then “contract” language is not load-bearing.

### 10.4 Latency and distortion accounting are ignored

If transfer is treated as frictionless, current, or fully faithful by default, the model is conceptually dishonest.

### 10.5 The graph-neural layer adds no measurable lift

If a flat baseline, single-scale model, or unconstrained message-passing model performs just as well with equal budget, this architecture should not be promoted as an explanatory advance.

### 10.6 Metaphor replaces benchmark evidence

If the framing remains elegant but does not produce clearer falsification or stronger results, it should stay at the level of conceptual scaffolding.

---

## 11) Benchmark and experiment requirements

A claim that this architecture matters should be judged against explicit baselines.

### 11.1 Minimum baseline set

Compare against:

1. **single-scale baseline**
   - no explicit temporal frame structure.

2. **multiframe unconstrained baseline**
   - frame structure exists, but no potential-flow contracts are enforced.

3. **neighbor-only contract model**
   - the proposed architecture.

### 11.2 Required ablations

At minimum, test:

- no contract projection,
- no shared latent coordinate space,
- no cross-frame coupling,
- unrestricted all-to-all coupling,
- latency/distortion terms removed.

### 11.3 Minimum metric set

Track:

- cross-frame prediction error,
- contract violation rate,
- coherence gain over baseline,
- robustness under temporal perturbation,
- latency-adjusted utility,
- and interpretability / inspection burden where measurable.

### 11.4 Promotion rule

The architecture should not be promoted beyond `REVIEW` unless it shows:

- measurable lift over declared baselines,
- robust behavior over a nontrivial threshold window,
- and no conflict with hard causal or physical gates.

---

## 12) Claim tiers

### Defensible now

- Predictive processing can be expressed as multiframe state revision with bounded cross-frame transfer.
- Graph-constrained message passing is a natural mechanism for neighbor-first multiscale coupling.
- Potential-flow contracts can serve as admissibility constraints on cross-frame transfer without violating causality by definition.
- Time-index-agnostic latent coordinates are a legitimate modeling convenience when explicitly treated as such.

### Plausible but unproven

- Contract-constrained cross-frame transfer will improve coherence, calibration, or stability over unconstrained coupling.
- This architecture will produce better interpretability because violations and budgets are made explicit rather than hidden in unrestricted latent mixing.
- Neurologically grounded multiscale predictive models may be more naturally expressed in this form than in flat predictive architectures.

### Speculative

- This architecture reveals a deep general law of intelligence.
- The same structure extends cleanly from engineered systems to cognition to fundamental physics without substantial revision.
- “Potential-flow contracts” capture more than a useful design scaffold in currently untested domains.

---

## 13) Documentation and implementation guidance

Near-term, this document should be used in three ways.

### 13.1 As a doc-level hygiene tool

Use it to keep multiscale predictive language disciplined:

- define the graph,
- define the contract,
- define the residual,
- define the latency/distortion burden,
- and define the benchmark.

### 13.2 As a simulation design scaffold

Use it to specify toy experiments where:

- multiple temporal frames must coordinate,
- prediction must survive delayed transfer,
- and unconstrained latent sharing can be compared against contract-bounded transfer.

### 13.3 As a promotion gate

Use it to block premature upgrades from:

- evocative concept
- to canonical mechanism claim.

The burden of proof remains empirical.

---

## 14) Suggested next actions

1. Add a row to `docs/theory-implementation-matrix.md` for this bridge architecture.
2. Create a toy benchmark with fast/meso/slow frame coupling under controlled latency and distortion.
3. Define one explicit contract residual function and at least one simpler null baseline.
4. Add short cross-links from `11` and `13` pointing here as the predictive-processing bridge doc.

---

## 15) Summary

This document gives Sandy Chaos a disciplined place to state a stronger computational idea that has been forming implicitly across several lanes.

The core proposal is simple:

- predictive processing may be distributed across temporal frames,
- frame interaction should be neighbor-first,
- transfer should be graph-constrained and contract-bounded,
- and latent alignment should be treated as a modeling device rather than an ontological shortcut.

If this architecture proves useful, it will do so by surviving comparison against simpler baselines.
If it fails, it should fail cleanly, by showing that the extra structure adds no explanatory or predictive leverage.
