# 11 Potential-Flow Contracts

_Legacy working labels: "Geodesic Hydrology Contracts" and "Geometric Transport Contracts"._

## 1) Purpose

This note defines a speculative proposal for Sandy Chaos:

> **contracts as potential-driven transport laws for information flow**, not just payout scripts for terminal predictions.

The earlier **geodesic hydrology** language was useful as an intuition pump, but it does not cleanly mirror the mathematical structure we actually want. The strongest current formulation is:

- **Potential-Flow Contracts** as the umbrella name,
- **weighted state geometry** as the transport substrate,
- **contract head / potential** as the high-versus-low ordering over that substrate,
- and **path-functional evaluation** as the scoring layer over realized trajectories.

So the hydrology and thermodynamic imagery can remain helpful as intuition, but the technical framing should be led by:

- explicit state geometry,
- potential fields,
- mobility / permeability structure,
- dissipative transport,
- and path-dependent reward functionals.

**Status:** this document is a **speculative proposal and rigor scaffold**, not a validated canonical result. Any operational reliance must remain consistent with the [Assumptions Register](assumptions_register.md), especially the quarantine rule in **A-013**.

---

## 2) Core idea (plain language)

Most program/agent contracts reward a final answer.

This proposal instead rewards **path quality over time**:

- reduce uncertainty and unresolved objective load,
- maintain calibration and stability under perturbation,
- stay resource-bounded,
- avoid harmful externalities,
- preserve causal and physical admissibility.

So value is earned by **good dynamics**, not one-shot luck.

The intended picture is:

1. states live in a structured space,
2. that space has an effective **up/down** ordering induced by a scalar contract potential,
3. geometry and mobility determine how descent can occur,
4. and the contract rewards trajectories that descend well without gaming, instability, or hidden costs.

This is why **potential-flow** is the right umbrella term: the proposal is about descent under a declared head / potential field, not about metaphorical water language for its own sake.

---

## 3) Boundaries inherited from project foundations

This proposal is admissible only if it remains inside Sandy Chaos hard constraints:

- no operational retrocausality,
- no superluminal signaling assumptions,
- no metaphor presented as mechanism without a stateful mapping,
- no deployment-policy promotion from speculative claims,
- no curvature/geodesic rhetoric treated as load-bearing unless explicit evidence exists.

See `FOUNDATIONS.md` markers **C1/I1/P1/P2/O3**, `docs/01_foundations.md`, and the support limits recorded in `docs/assumptions_register.md`.

---

## 4) Assumptions-register alignment

This note currently depends on the following assumptions and should be read at that support level:

- **A-001 / A-002** — no ontic backward-causal channel; any apparent future-like advantage must reduce to forward dynamics, inference, and lawful propagation.
- **A-003** — boundary/legibility scaffolds may be used as modeling aids, but not promoted as established mechanism.
- **A-005** — geometry may be structurally useful, but **curvature-specific leverage is not yet established**; if Kerr-specific leverage fails, this proposal should downscope to a flatter transport/control picture.
- **A-011** — claim tiers and marker gates must constrain how this note is described and promoted.
- **A-012** — empirical success requires lift over declared baselines, not elegance of language.
- **A-013** — this proposal remains quarantined as a speculative design layer until it cashes out in explicit models and tests.

In other words: this note may be useful for structuring future work, but it does **not** currently upgrade any project claim above `Speculative` / `Review` on its own.

---

## 5) Terminology migration (legacy metaphor → operational language)

To keep the language congruent with the math, use the following preferred mappings:

- **contract head** → scalar potential ordering states from higher to lower unresolved load
- **potential-flow** → descent dynamics driven by gradients of contract head
- **weighted state geometry** → the metric, topology, admissibility structure, and anisotropic costs of the state space
- **mobility / permeability operator** → the structure that determines which downhill directions are available and how easily they can be traversed
- **path-functional evaluation** → scoring a whole trajectory rather than only the endpoint
- **irreversible commitment boundary** → a one-way protocol boundary induced by locks, stakes, deadlines, or other irreversible rules

Legacy metaphor mappings may still be used as intuition:

- **droplet** → localized information/work packet with explicit state and provenance
- **elevation / head** → objective-risk-uncertainty potential
- **flow** → transport dynamics under update rules and constraints
- **friction** → compute, latency, energy, and externality costs
- **reservoir** → shared buffer / memory / coordination state
- **flood / turbulence** → instability, adversarial amplification, or unbounded variance

Preferred naming in future prose:

- **potential-flow contracts**
- **path-functional coordination contracts**
- **geometric transport contracts**

Avoid letting the hydrology language stand alone without the operational translation.

---

## 6) Formal foundations: weighted geometry, contract head, and dissipative transport

This section inherits the shared notation bridge defined in **[02 Tempo Tracer Protocol](02_tempo_tracer_protocol.md)**. In particular, the scored state $z_t$ should be read as the augmented forward-causal state, which may include the observer-local decomposition from **[03 Micro-Observer & Agency](03_micro_observer_agency.md)**:

$$
z_t \sim (L_t, O_t, S_t, A_t, h_t)
$$

The cleanest mathematical skeleton is the tuple:

$$
(M,\; g,\; K,\; H,\; B_\lambda,\; \Omega)
$$

Where:

- $M$ is the state space,
- $g$ is a declared metric / topology / geometric structure on that space,
- $K$ is a mobility or permeability operator,
- $H$ is the scalar **contract head** field,
- $B_\lambda$ is the observer-coupling control / forcing term (as operationalized in **[03 Micro-Observer & Agency](03_micro_observer_agency.md)**),
- $\Omega$ is the penalty / slashing / hard-constraint layer.

### 6.1 State space and path dependence

Let the system evolve on a state space $M$. If path dependence matters explicitly, use an augmented state:

$$
z_t = (x_t, h_t)
$$

where:

- $x_t$ is the ordinary system state,
- $h_t$ is a memory/history state encoding relevant path information.

This keeps path dependence forward-causal rather than mystical: history enters because it is part of the present state description.

### 6.2 Contract head: the up/down ordering

The key scalar quantity is the **contract head**:

$$
H(z,t) = w_u U(z,t) + w_o O(z,t) + w_r R(z,t) + w_e E(z,t)
$$

Where:

- $U$: uncertainty load,
- $O$: objective deficit,
- $R$: risk / instability / coordination fragility,
- $E$: externality or resource burden,
- $w_*$ are nonnegative weights declared pre-run.

This field provides the effective **vertical ordering** of the state space:

- high $H$ = unresolved / expensive / unstable states,
- low $H$ = more resolved / lower-burden / better-coordinated states.

This is the part of the theory that is analogous to:

- gravitational height,
- hydraulic head,
- temperature / free-energy gradients,
- or pressure differences.

### 6.3 Why geometry is part of the transport law

The important correction is:

> the transport structure is **not** geometry alone, and **not** potential alone, but the coupled structure $(g, K, H)$.

- The **head field** $H$ tells us what counts as high versus low.
- The **geometry** $g$ tells us what counts as near, steep, or costly.
- The **mobility** $K$ tells us which downhill directions are actually traversable, and with what ease.

So geometry is not decorative. It helps determine what "downhill" means and what routes are admissible. But geometry is still not sufficient by itself: without a head field there is no ordered descent target, only structure.

This is why the right formulation is:

> **Potential-Flow Contracts are dissipative transport on a weighted state geometry.**

### 6.4 Micro-scale evolution law

For single-trajectory dynamics, the natural equation is:

$$
\dot{z}_t = -K_{z_t}\,\mathrm{grad}_g H(z_t,t) + B_\lambda(z_t,t)
$$

Interpretation:

- the system tends toward lower contract head,
- the metric $g$ determines what the gradient means,
- the mobility $K$ filters which descent directions are accessible,
- and $B_\lambda$ captures observer-coupled control, forcing, or non-potential steering.

### 6.5 Collective transport law

For ensemble or market-style behavior, let $\rho(z,t)$ denote a state density. Then:

$$
\partial_t \rho + \nabla\cdot J = s-d
$$

with transport flux:

$$
J = -\rho\,K\nabla_g H - D\nabla_g \rho + B_\lambda\rho
$$

where:

- $D$ is a diffusion / uncertainty tensor,
- $s,d$ are source/sink terms,
- and the first term is the potential-driven transport term.

This is the collective version of the same theory:

- directed descent,
- noise/spread,
- protocol steering,
- and open-system injection/removal.

### 6.6 Tempo-tracing observables as empirical readouts

The transport layer should be connected to empirical observables through the Tempo Tracing metrics defined in **[02 Tempo Tracer Protocol](02_tempo_tracer_protocol.md)**:

$$
C_{A\to B}(\Delta\tau),\quad C_{B\to A}(\Delta\tau),\quad \mathcal{A}(\Delta\tau)=C_{A\to B}(\Delta\tau)-C_{B\to A}(\Delta\tau)
$$

Interpretation in this contract framework:

- $C_{A\to B}(\Delta\tau)$ and $C_{B\to A}(\Delta\tau)$ are directional transport-capacity readouts over proper-time offset,
- $\mathcal{A}(\Delta\tau)$ measures asymmetry induced by geometry, mobility, and observer-coupled forcing,
- these are **measurement-layer observables**, not the reward function themselves,
- but they help determine whether the proposed transport structure has any empirical leverage worth scoring.

So the connective tissue across the docs is:

- **[02](02_tempo_tracer_protocol.md)** measures transport asymmetry,
- **[03](03_micro_observer_agency.md)** defines the observer-coupling term $B_\lambda$,
- **this document (11)** defines the head field $H$ and path-functional evaluation of trajectories generated under those dynamics.

### 6.7 Free-energy-like functional

A natural global functional is:

$$
\mathcal{F}[\rho,t] = \int \rho(z,t) H(z,t)\,dz + \tau \int \rho(z,t)\log\rho(z,t)\,dz
$$

with $\tau \ge 0$ as entropy regularization strength.

Under dissipative conditions, the system should tend to reduce $\mathcal{F}$ or at least exhibit an explicit balance law:

$$
\dot{\mathcal{F}} = \dot{\mathcal{F}}_{diss} + \dot{\mathcal{F}}_{in} - \dot{\mathcal{F}}_{out}
$$

This is the most rigorous bridge to thermodynamic or heat-transfer intuition: the analogy becomes meaningful only once the free-energy-like functional is explicit.

### 6.8 Contract payout as a path functional

For participant $i$ over horizon $[0,T]$:

$$
R_i[\gamma] = \int_0^T \left[\alpha\,\big(-\dot{\mathcal{F}}_i(t)\big)_+
+ \beta\,\Delta I_i(t)
- \gamma\,C_i(t)
- \xi\,X_i(t)
+ \delta\,S_i(t)\right]dt - \Omega_i
$$

Where:

- $(-\dot{\mathcal{F}}_i)_+$: positive contract-head / free-energy reduction contribution,
- $\Delta I_i$: information-gain contribution over declared baseline,
- $C_i$: compute/latency/energy cost term,
- $X_i$: distortion/externality term,
- $S_i$: robustness/recovery contribution,
- $\Omega_i$: slashing penalties (fraud/inconsistency/non-delivery).

This is what makes the contract explicitly **path-functional** rather than endpoint-only.

---

## 7) Geometry, geodesics, and what is actually load-bearing

Geodesic language can still appear, but it is **not** the default center of the theory.

Reference form:

$$
\ddot{x}^k + \Gamma^k_{ij}(x)\dot{x}^i\dot{x}^j = 0
$$

This is useful when describing:

- extremal/autoparallel motion,
- least-action or inertial limits,
- or geometry-first special cases.

But the core mechanism here is instead:

$$
\dot{z}_t = -K_{z_t}\,\mathrm{grad}_g H(z_t,t) + B_\lambda(z_t,t)
$$

So the priority order is:

1. **contract head / potential** gives the vertical ordering,
2. **geometry + mobility** determine admissible descent structure,
3. **dissipation / forcing** determine actual transport,
4. **path-functional reward** evaluates the resulting trajectory.

This means:

- geometry is **part of the transport law itself**,
- but curvature-specific rhetoric is not yet proven to add empirical lift,
- and geodesic language should remain optional unless a geometry-specific benchmark justifies it.

Non-negotiable interpretation rules:

- geodesic terminology is **secondary** unless a geometry-specific leverage claim is actually demonstrated,
- high-curvature / horizon language is **illustrative**, not evidence of exotic physics,
- if curvature-specific leverage is not shown, this proposal should be described in the cleaner language of **weighted geometry, contract head, and dissipative transport**.

---

## 8) Compatibility check with current repo discipline

### Compatible with existing direction

1. **Forward-causal discipline**
   - Matches `docs/01_foundations.md` if all updates are local-in-time and causal.
2. **Observer + agency framing**
   - Aligns with `docs/03_micro_observer_agency.md` when rewards use measurable observables only.
3. **Prediction rigor**
   - Aligns with `docs/prediction-protocol.md` when scoring rules and baselines are pre-registered.
4. **Claim-tier policy**
   - Fits `FOUNDATIONS.md` if speculative layers are explicitly quarantined.

### Likely incompatibilities (must be actively prevented)

1. **Retrocausal language drift**
   - Incompatibility: any phrasing implying future events physically update past states.
   - Required rewrite: "forecasting lead from asymmetry + inference".

2. **Curvature as free magic**
   - Incompatibility: talking as though geometry-specific language automatically proves advantage.
   - Required rewrite: weighted geometry may be structural, but geometry-specific lift must still be benchmarked.

3. **Perfect-reflection absolutism**
   - Incompatibility: implies impossible omniscient modeling.
   - Required rewrite: bounded calibration targets with explicit error bars.

4. **Metaphor treated as mechanism**
   - Incompatibility: fluid/horizon language without state-variable mapping.
   - Required rewrite: enforce O3 mapping discipline before implementation claims.

5. **Speculation driving automation policy**
   - Incompatibility: Tier-3 narratives used for auto-promotion.
   - Required rewrite: keep this note as hypothesis-generation / design-scaffold material only.

---

## 9) Claim tiers for this proposal

### Defensible now

- Path-functional reward design is a coherent mechanism-design extension of existing prediction-protocol ideas.
- Potential-flow language can be kept causality-safe when tied to explicit state variables, head fields, transport laws, and benchmark criteria.
- Weighted geometry is a mathematically legitimate part of the transport structure, provided it is declared rather than smuggled in metaphorically.

### Plausible but unproven

- This mechanism can reduce one-shot gaming and improve multi-agent coordination stability versus terminal-only payout schemes.
- Explicit head-driven transport may give better control over coordination bottlenecks than flat endpoint-only reward schemes.

### Speculative

- Strong claims about consciousness, deep ontological equivalence, or universal physical finality.
- Any claim that curvature-specific or horizon-specific language is doing real explanatory work absent explicit comparative evidence.

---

## 10) Falsification hooks (required before strong claims)

1. **Anti-gaming test**
   - Compare against terminal-scoring baseline under adversarial agents.
   - Failure: no exploitability reduction.

2. **Coordination-welfare test**
   - Measure global objective and variance under equal budget.
   - Failure: no welfare gain or higher instability than baseline.

3. **Robustness-under-shock test**
   - Inject perturbations and measure recovery time/calibration.
   - Failure: slower recovery despite higher complexity.

4. **Cost-realism test**
   - Include full compute/latency/energy accounting.
   - Failure: gains disappear once true costs are included.

5. **Geometry-necessity test**
   - Compare weighted-geometry formulations against a flatter transport-control baseline.
   - Failure: no meaningful lift from the geometry-specific layer.

6. **Path-dependence necessity test**
   - Compare path-functional scoring against memoryless endpoint scoring under equal information and budget.
   - Failure: no measurable advantage from the path-dependent layer.

---

## 11) Minimal implementation roadmap (proposal)

### Phase A (doc + simulation spec)

- Define a toy 2-agent / 2-task landscape with explicit $H$, $K$, $B_\lambda$, $J$, and $R_i$.
- Make path dependence explicit through an augmented state or memory variable.
- Connect the toy landscape to Tempo Tracing observables $C_{A\to B}(\Delta\tau)$, $C_{B\to A}(\Delta\tau)$, and $\mathcal{A}(\Delta\tau)$.
- Add or refine the matrix row for this direction.
- Keep decision state at `REVIEW` until comparative evidence exists.

### Phase B (protocol prototype)

- Extend packet/contract schema with optional path-score metadata.
- Add verifier checks for attribution and consistency.
- Formalize what parts of $H$ are observable versus inferred.

### Phase C (economy stress tests)

- adversarial collusion tests,
- stake/slashing sensitivity sweeps,
- randomized audit policies,
- flat-baseline versus weighted-geometry comparison,
- path-functional versus endpoint-only comparison.

Human review gate required at each phase boundary.

---

## 12) Relationship to existing docs

- `FOUNDATIONS.md` — hard governance + marker gates
- `docs/01_foundations.md` — causality contract
- `docs/02_tempo_tracer_protocol.md` — transport observables, packet semantics, and directional asymmetry metrics over $\Delta\tau$
- `docs/03_micro_observer_agency.md` — observer-coupling term $B_\lambda$ and operational agency invariants
- `docs/assumptions_register.md` — central dependency ledger; especially **A-005**, **A-011**, **A-012**, **A-013**
- `docs/prediction-protocol.md` — pre-registration / scoring / novelty rules
- `docs/theory-implementation-matrix.md` — traceability + decision ledger (`T-011`)

This note is intended as a **speculative rigor-preserving expansion path**, not a bypass of existing constraints and not a canonical framework addition until validated.
