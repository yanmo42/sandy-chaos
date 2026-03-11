# 02 Tempo Tracer Protocol

## 1) Purpose

This document defines the operational layer of Tempo Tracer: how signaling, timing, and validation work under strict causality constraints.

The objective is **forecasting advantage without retrocausality**.

---

## 2) Channel model (minimal formal core)

At the shared formal layer used across **[02 Tempo Tracer Protocol](02_tempo_tracer_protocol.md)**, **[03 Micro-Observer & Agency](03_micro_observer_agency.md)**, and **[11 Potential-Flow Contracts](11_geodesic_hydrology_contracts.md)**, Tempo Tracing measures forward-causal transport on an observer-coupled state space.

A useful modeling tuple is:

$$
\Theta = (M,\; g,\; K,\; H,\; B_\lambda,\; P,\; \Delta\tau,\; \rho)
$$

Where:

- $M$: declared state space (optionally augmented with memory/history variables),
- $g$: metric / topology / timing geometry,
- $K$: mobility / permeability / admissibility operator,
- $H$: scalar head / potential field ordering states by unresolved load,
- $B_\lambda$: observer-coupling control term parameterized by coupling scale $\lambda$,
- $P$: packet schema,
- $\Delta\tau$: proper-time offset coordinate,
- $\rho$: state or packet density for ensemble views.

At this shared layer, the generic forward-causal transport law is:

$$
\dot{z}_t = -K_{z_t}\,\mathrm{grad}_g H(z_t,t) + B_\lambda(z_t,t)
$$

or, for collective behavior,

$$
\partial_t \rho + \nabla\cdot J = s-d,
\qquad
J = -\rho K\nabla_g H - D\nabla_g\rho + B_\lambda\rho
$$

Interpretation of ownership across docs:

- **this document (02)** defines the transport/packet/timing observables,
- **[03](03_micro_observer_agency.md)** defines the observer-coupling term $B_\lambda$ and its local observables,
- **[11](11_geodesic_hydrology_contracts.md)** defines the head field $H$ and path-functional reward layer.

Tempo Tracing does **not** claim that every term in this tuple is fully implemented in one production simulator today. This is the connective tissue that makes the causal core legible across the three documents.

### 2.1 Shared notation bridge (02 / 03 / 11)

To prevent symbol drift, the shared symbols should be interpreted as follows:

| Shared symbol | Shared-layer meaning | Local reading in `02` | Local reading in `03` | Local reading in `11` |
|---|---|---|---|---|
| $z_t$ | present augmented state | packet/channel state at step $t$ | may bundle $(L_t, O_t, S_t, A_t, h_t)$ | trajectory state being scored |
| $M$ | total state space | timing/channel state space | observer-environment-action state space | contract-evaluation state space |
| $g$ | metric / topology / geometry | timing / propagation geometry | observer-local interaction geometry | weighted state geometry |
| $K$ | mobility / admissibility structure | transport / attenuation / routing structure | bounded steerability of future updates | mobility / permeability operator |
| $H$ | scalar head / potential | abstract ordering field for transport, not yet a primary implementation object here | inherited/exogenous structure, not yet a learned field in current implementation | explicit contract head |
| $B_\lambda$ | bounded forcing / control term | source of transport asymmetry over $\Delta\tau$ | realized concretely as observer coupling $\Phi(x,t)$ | observer-coupled steering term inside contract dynamics |
| $P$ | packet / information object | minimal packet schema $P_{min}$ | measurement/intervention payloads may influence it but do not redefine it | optional future carrier for path-score metadata |
| $\Delta\tau$ | proper-time offset coordinate | primary asymmetry coordinate | contributes to predictive-horizon and frame-asymmetry diagnostics | empirical readout that may later enter scoring |
| $\rho$ | density / ensemble view | packet profile / transport distribution | ensemble of observer-coupled trajectories | state density in free-energy / payout analysis |

Rule of thumb:

- **02** measures transport asymmetry,
- **03** defines the observer-coupling contribution,
- **11** defines the potential/head field and path-functional scoring.

When a symbol appears in more than one doc, default to the **shared-layer meaning first** and the **local specialization second**.

### 2.2 Kerr-specific channel realization

A current channel-specific realization models propagation through a curved-spacetime medium as:

$$
Y = \mathcal{F}_{\text{Kerr}}(X, u, n)
$$

- $X$: initial photon/observable ensemble
- $u$: controlled modulation schedule
- $n$: background noise
- $Y$: received observables

Null-geodesic consistency condition:

$$
\mathcal{H}_{null} = \tfrac{1}{2}g^{\mu\nu}p_\mu p_\nu \approx 0
$$

If this fails numerically, the run is invalid.

---

## 3) Communication modes

### Mode A — Direct Light Path

- Baseline line-of-sight signaling
- Light-speed limited
- Usually highest fidelity / easiest attribution

### Mode B — Shared Medium (Vortex / BH-mediated)

- Both parties encode and decode through a shared geometric channel
- Latency and quality can be asymmetric (A→B differs from B→A)
- Most relevant for "future-like" timing asymmetry effects

### Mode C — Archival / Beacon

- Long-lived structured signatures in outside-horizon observables
- Intended for delayed recovery and decoding

---

## 4) Timing planes and packet semantics

We separate three timing layers:

- External reference time: $t$
- Observer-local clocks: $\tau_A, \tau_B$
- Protocol/meta-time: $\sigma$

Current minimal packet schema:

$$
P_{min} = \{payload, \tau_{send}, \sigma_{send}, confidence, checksum\}
$$

Planned optional trust/interpretation extensions may add fields such as validity windows, boundary tags, narrative context, or audit traces, but those are not baseline requirements of the current implementation.

Interpretation still requires all three planes: data, timing, trust.

---

## 5) Causality-safe interpretation rule

Tempo Tracer allows:

- forward physical transport,
- observer-dependent timing asymmetry,
- anticipatory behavior based on expected future inference.

Tempo Tracer forbids:

- ontic backward causation,
- superluminal operational claims,
- in-horizon message recovery claims.

"Future-like" effects must be reducible to forward dynamics + timing asymmetry + inference.

---

## 6) Falsification-first metrics

Minimum validation stack:

1. **Detection performance**: ROC/AUC for controlled modulation vs baseline
2. **Distributional shift**: KL divergence between natural and modulated observables
3. **Information transfer**: lower bound on $I(U;Y)$
4. **Temporal consistency**:

$$
E_{align}=\left|(\tau_{recv}-\tau_{send})-\tau_{expected}\right|
$$

5. **Forecast reliability**: calibration curves, Brier score, false alarm rate

If reproducibility/significance thresholds fail, the claim fails.

---

## 7) Protocol workflow (practical)

1. Define claim tier (defensible / plausible / speculative).
2. Specify encoding schedule $u$ and baseline conditions.
3. Run geodesic quality checks and reject invalid trajectories.
4. Decode with uncertainty-aware inference.
5. Audit timing alignment, trust metadata, and reproducibility.

---

## 8) Relationship to other docs

- **[01 Foundations](01_foundations.md)** explains the causal boundary and epistemic retro-influence distinction.
- **[03 Micro-Observer & Agency](03_micro_observer_agency.md)** supplies the observer-coupling term $B_\lambda$ and its local observables.
- **[11 Potential-Flow Contracts](11_geodesic_hydrology_contracts.md)** supplies the head field $H$ and path-functional evaluation layer that sit on top of these transport dynamics.
- **[07 Agentic Automation Loop](07_agentic_automation_loop.md)** maps these protocol ideas into live execution loops (systemd cadence, orchestration contracts, dispatch telemetry, and productivity gating).
- **[Math Appendix](math_appendix.md)** contains extended equation references.
- **[10 Tempo Tracing Refactor Note](10_tempo_tracing_refactor_note.md)** records the planned migration to process-first terminology ("Tempo Tracing").

## 9) Temporal-frame communication dynamics (new focus)

To operationalize cross-frame communication, protocol evaluation should compute directional capacity conditioned on proper-time offset:

$$
C_{A\to B}(\Delta\tau),\quad C_{B\to A}(\Delta\tau)
$$

with asymmetry metric:

$$
\mathcal{A}(\Delta\tau)=C_{A\to B}(\Delta\tau)-C_{B\to A}(\Delta\tau)
$$

Interpretation rules:

- Nonzero $\mathcal{A}$ is a directional communication asymmetry, not retrocausality.
- Claims require null-model comparison (no observer coupling / flat timing baseline).
- Report confidence intervals and robustness across noise regimes.
- In the shared formal layer, these are **empirical readouts of transport asymmetry over $\Delta\tau$**, not stand-alone metaphysical quantities.
- **[03](03_micro_observer_agency.md)** explains how observer coupling contributes the bounded forcing term $B_\lambda$; **[11](11_geodesic_hydrology_contracts.md)** explains how these traced transport patterns may later be scored by path-functional contract logic.

Falsification harness (implemented in automated tests):

- **Null model**: symmetric bidirectional attenuation (`backward_attenuation = 1.0`) with matched source drives predicts asymmetry ratio near 1.
- **Coupled model**: attenuated reverse path (`backward_attenuation < 1`) predicts a stable deviation from 1 while preserving forward-time packet propagation.
- **Profile-level falsification**: under shared $\Delta\tau$ bins, the null model keeps low $\|\mathcal{A}\|_1$ while the coupled model yields a clearly larger $\|\mathcal{A}\|_1$.
- Causality hard-check: tests inject synthetic packets with $\Delta\tau \le 0$ and verify they contribute zero profile mass.
- Reject any interpretation that requires influence from future states; all packet handling is computed from current/past state only.

Implementation target: compute an asymmetry surface over $(\Delta\tau,\lambda)$ where $\lambda$ is observer coupling gain, and publish failure conditions for each regime.

## 10) Current implementation mapping

`nfem_suite.simulation.communication.VortexChannel` now exposes
`compute_temporal_frame_metrics(...)` with:

- `C_A_to_B` corresponding to $C_{A\to B}(\Delta\tau)$
- `C_B_to_A` corresponding to $C_{B\to A}(\Delta\tau)$
- `asymmetry` corresponding to $\mathcal{A}(\Delta\tau)$
- optional `asymmetry_surface` over $(\Delta\tau, \lambda)$ via `coupling_values`

Causality guardrail: only packets with strictly positive propagation delay
($\Delta\tau > 0$) contribute to these metrics. Input bins are required to be
finite, strictly increasing, and nonnegative to prevent invalid cross-frame
indexing.
