# 11 Geodesic Hydrology Contracts

## 1) Purpose

This note defines a new proposal for Sandy Chaos:

> **contracts as local physics for information flow**, not just payout scripts for terminal predictions.

The motivating intuition is hydrological: informational state behaves like droplets moving through a shaped landscape, tending toward lower potential under constraints.

This document is a **proposal + rigor scaffold**, not a validated implementation.

---

## 2) Core idea (plain language)

Most program/agent contracts reward a final answer.

This proposal instead rewards **path quality over time**:

- reduce uncertainty and unresolved objective load,
- maintain calibration/stability under perturbation,
- stay resource-bounded,
- avoid harmful externalities,
- preserve causal and physical admissibility.

So value is earned by **good dynamics**, not one-shot luck.

The droplet/water language is treated as analogy only; the operational model is energy + flux based.

---

## 3) Boundaries inherited from project foundations

This proposal is admissible only if it remains inside Sandy Chaos hard constraints:

- no operational retrocausality,
- no superluminal signaling assumptions,
- no metaphor presented as mechanism without stateful mapping,
- no deployment policy promotion from speculative claims.

See `FOUNDATIONS.md` markers **C1/I1/P1/P2/O3** and `docs/01_foundations.md` causality boundary.

---

## 4) Hydrology mapping (metaphor → operational variable)

- **Droplet** → localized information/work packet with explicit state and provenance
- **Elevation/potential** → unresolved uncertainty + unmet objective + risk load
- **Flow** → state evolution under update rule and constraints
- **Friction** → compute/latency/energy/externality costs
- **Channel geometry** → protocol/interface/market topology
- **Reservoir** → shared memory/coordination buffer
- **Flood/turbulence** → instability, adversarial amplification, or unbounded variance

No term is allowed to remain purely poetic; each must map to measurable state variables before implementation claims.

---

## 5) Minimal formalization sketch (energy-first)

Let program/agent state evolve on an information manifold with coordinates $x$ and time $t$.

### 5.1 Potential and global energy functional

Define a scalar potential:

$$
\Phi(x,t) = w_u U(x,t) + w_o O(x,t) + w_r R(x,t)
$$

Where:

- $U$: uncertainty load,
- $O$: objective deficit,
- $R$: risk/externality exposure,
- $w_*$ are nonnegative weights declared pre-run.

Define a free-energy-like system functional:

$$
\mathcal{E}[\rho,t] = \int \rho(x,t)\,\Phi(x,t)\,dx + \tau \int \rho(x,t)\log\rho(x,t)\,dx
$$

with $\rho(x,t)$ as state-density and $\tau\ge0$ as entropy regularization strength.

### 5.2 Flux dynamics (with Gaussian closure option)

Let $\rho(x,t)$ obey continuity:

$$
\partial_t \rho + \nabla\cdot J = s-d
$$

with drift-diffusion flux:

$$
J = -\mu\,\rho\,\nabla_g\Phi - D\nabla_g\rho + B(x,t)\rho
$$

where:

- $\mu$: descent responsiveness,
- $D$: diffusion/noise tensor,
- $B$: protocol-induced drift/control,
- $s,d$: source/sink processes.

For Gaussian-style flux approximations, local uncertainty can be represented by covariance $\Sigma(x,t)$ and absorbed into $D$ (or an equivalent closure), enabling practical estimation of transport under noisy dynamics.

In closed, dissipative settings this should induce non-increasing energy under suitable assumptions; in open settings track explicit energy balance:

$$
\dot{\mathcal{E}} = \dot{\mathcal{E}}_{diss} + \dot{\mathcal{E}}_{in} - \dot{\mathcal{E}}_{out}
$$

### 5.3 Contract payout as path functional

For participant $i$ over horizon $[0,T]$:

$$
R_i = \int_0^T \left[\alpha\,\big(-\dot{\mathcal{E}}_i(t)\big)_+
+ \beta\,\Delta I_i(t)
- \gamma\,C_i(t)
- \xi\,X_i(t)
+ \delta\,S_i(t)\right]dt - \Omega_i
$$

Where:

- $(-\dot{\mathcal{E}}_i)_+$: positive energy reduction contribution,
- $\Delta I_i$: information-gain contribution over declared baseline,
- $C_i$: compute/latency/energy cost term,
- $X_i$: distortion/externality term,
- $S_i$: robustness/recovery contribution,
- $\Omega_i$: slashing penalties (fraud/inconsistency/non-delivery).

---

## 6) Geodesic + black-hole communication interpretation (computational metaphor)

This proposal can be coupled to existing geodesic language as follows (with terminology discipline):

- **geodesic (modeling sense)**: an extremal/autoparallel trajectory under a declared metric + connection (not automatically a shortest path in every geometry).
- **routing geodesic analogue**: a path minimizing a declared communication/action functional in the modeled manifold.
- **high-curvature region**: a zone of high sensitivity to perturbation; "attraction" should be attributed to potential + dissipation terms, not curvature alone.
- **event-horizon analogue**: a one-way commitment boundary induced by protocol irreversibility (e.g., lock/stake/hash-time gate), not a literal GR horizon.
- **boundary readout (holographic analogue)**: compressed, auditable summary variables exposed at an interface boundary.

Reference forms (for terminology hygiene):

$$
\ddot{x}^k + \Gamma^k_{ij}(x)\dot{x}^i\dot{x}^j = 0
$$

(geodesic/autoparallel equation under chosen connection) versus

$$
\dot{x} = -\nabla_g \Phi(x,t)
$$

(dissipative gradient flow under metric $g$).

Non-negotiable interpretation rule:

- "black-hole communication" is a **modeling metaphor for constrained routing and compression**, not a claim of physical retro-signaling.

---

## 7) Ideological compatibility check (current repo)

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

2. **"Perfect reflection" absolutism**
   - Incompatibility: implies impossible omniscient modeling.
   - Required rewrite: bounded calibration targets with explicit error bars.

3. **Consciousness overclaim**
   - Incompatibility: treating flow behavior as proof of intrinsic consciousness.
   - Required rewrite: use operational proxies only unless separate evidence exists.

4. **Metaphor treated as mechanism**
   - Incompatibility: hydrology terms without state-variable mapping.
   - Required rewrite: enforce O3 mapping checklist before implementation claims.

5. **Speculation driving automation policy**
   - Incompatibility: Tier-3 narratives used for auto-promotion.
   - Required rewrite: keep Tier-3 as hypothesis generation only.

---

## 8) Claim tiers for this proposal

### Defensible now

- Path-integral reward design is a coherent mechanism-design extension of existing prediction protocol ideas.
- Hydrology/geodesic language can be made causality-safe when mapped to explicit state dynamics.

### Plausible but unproven

- This mechanism can reduce one-shot gaming and improve multi-agent coordination stability versus terminal-only payout schemes.

### Speculative

- Strong claims about consciousness, deep ontological equivalence, or universal physical finality.

---

## 9) Falsification hooks (required before strong claims)

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

---

## 10) Minimal implementation roadmap (proposal)

### Phase A (doc + simulation spec)

- Define a toy 2-agent/2-task landscape with explicit $\Phi, J, R_i$.
- Add matrix row and prediction artifacts for benchmarks.

### Phase B (protocol prototype)

- Extend packet/contract schema with optional path-score metadata.
- Add verifier checks for attribution and consistency.

### Phase C (economy stress tests)

- Adversarial collusion tests,
- stake/slashing sensitivity sweeps,
- randomized audit policies.

Human review gate required at each phase boundary.

---

## 11) Relationship to existing docs

- `FOUNDATIONS.md` — hard governance + marker gates
- `docs/01_foundations.md` — causality contract
- `docs/03_micro_observer_agency.md` — operational agency + ethics invariants
- `docs/prediction-protocol.md` — pre-registration/scoring/novelty rules
- `docs/theory-implementation-matrix.md` — traceability + decision ledger

This note is intended as a rigor-preserving expansion path, not a bypass of existing constraints.
