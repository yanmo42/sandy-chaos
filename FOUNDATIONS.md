# FOUNDATIONS.md

## Purpose

This document defines the **hard foundation contract** for Sandy Chaos.
It is the source of truth for what must remain coherent across:

- theory development,
- implementation and automation,
- validation and policy promotion.

The goal is to preserve elegance and rigor while scaling agentic iteration.

---

## 0) Scope and claim discipline

All claims in this project must be labeled as one of the following:

1. **Formal (F):** derivable from explicitly stated axioms/definitions.
2. **Computational (C):** provable over a model/program semantics (e.g., invariants, complexity, convergence bounds).
3. **Empirical (E):** testable against observations/simulations and therefore falsifiable.
4. **Speculative (S):** not yet derivable or testable; allowed only when clearly quarantined.

### Rule

- No implementation decision may rely on an unlabeled claim.
- Automation may only auto-promote changes grounded in F/C/E criteria.
- S claims may inspire experiments but cannot drive policy promotion.

---

## 1) Ontological primitives (minimal vocabulary)

The system ontology is intentionally compact:

- **Observer** `O`: an information-processing entity with state and update rule.
- **Substrate** `P`: physical medium carrying signals/states (classical, quantum, astrophysical).
- **State** `x_t`: system configuration at time `t`.
- **Action/Control** `a_t`: intervention applied by an observer/agent.
- **Channel** `K`: communication pathway with noise, delay, and capacity.
- **Noise** `η_t`: stochastic uncertainty from environment/model error.
- **Cost** `J`: objective including information gain, resource use, and constraint penalties.
- **Constraint set** `Γ`: causal/physical/computational admissibility boundaries.
- **Horizon** `H`: finite prediction/optimization window.
- **Evidence** `D`: logs, traces, metrics, tests supporting a claim.

### Ontology adequacy criterion (O1)

Any new concept must map to at least one primitive above (or extend ontology with a formal definition). If not, it remains speculative language.

---

## 2) Core dynamics (causal forward model)

All operational models must be representable as forward evolution:

`x_{t+Δ} = F_Δ(x_t, a_t, η_t; Γ)`

with observer updates:

`b_{t+Δ} = U(b_t, y_t, π_t)`

where `b_t` is belief/memory state and `y_t` is observation.

### Causality contract (C1)

No production claim or implementation may require operational dependence of present state on future intervention:

`P(x_t | do(a_{t+Δ}), I_t) = P(x_t | I_t)`

Interpretation: no ontic backward-causal channel is permitted.

### Operational-present axioms (N1–N3)

These axioms constrain any claim involving "real now" access, observer effects, sensory anchoring, or retrodictive reconstruction.

- **N1 — Bounded-now:** no observer has direct access to a latency-free global present. Observation is channel-limited, delayed, and noisy.
- **N2 — Measurement backaction:** measurement policy may perturb future admissible dynamics (possibly weakly), so sensing and intervention are generally coupled.
- **N3 — Causal admissibility:** prediction and retrodiction may be strong, but all physical state evolution remains forward-causal.

Reference form:

`y_i(τ_i) = M_i(x_{t-δ_i}, π_i) + ε_i`

`x_{t+Δ} = F_Δ(x_t, a_t, η_t; Γ) + B_λ(x_t, π_t, y_t)`

where `δ_i` is observer/channel latency, `π_i` is measurement policy, and `B_λ` is bounded observer-coupled backaction.

---

## 3) Information-theoretic constraints

All channel/observer designs must define:

- entropy budget `H(X)`,
- uncertainty reduction `I(X;Y)`,
- effective channel capacity `C_K`,
- error-rate target `ε` and coding/decoding assumptions.

### Marker I1 (capacity admissibility)

For a claimed signaling protocol with rate `R`:

- admissible only if `R ≤ C_K` under stated noise model.

### Marker I2 (inference gain)

A forecasting advantage claim must provide measurable gain over baseline:

`ΔI = I(target; observations_with_method) - I(target; baseline_observations) > 0`

with confidence interval and robustness checks.

---

## 4) Computational-theoretic constraints

Each algorithm/protocol used by the automation loop must declare:

- computational complexity (time/space),
- convergence/stability behavior (if iterative),
- failure modes and bounded rollback path.

### Marker C2 (resource-boundedness)

A loop policy is admissible only if expected compute/latency stays within configured envelope:

`E[T_cycle] ≤ T_max`, `E[M_cycle] ≤ M_max`, `E[E_cycle] ≤ E_max` (where measurable).

### Marker C3 (termination/stability)

For any auto-improvement routine, one of the following must be shown:

- termination guarantee, or
- bounded non-termination with watchdog/recovery policy.

### Marker C4 (semantic preservation)

Changes to formal-core modules must pass invariants/tests proving preserved semantics relative to declared contracts.

---

## 5) Physical admissibility (astral/astrophysical layer)

The project may model computation across astrophysical substrates, but only with explicit physical constraints:

- finite signal speed and relativistic delay,
- energy and thermodynamic cost,
- noise/decoherence and measurement limits,
- finite observer precision and synchronization limits.

### Marker P1 (relativistic consistency)

Any cross-frame claim must specify frame assumptions and preserve causal ordering under Lorentz-consistent interpretation.

### Marker P2 (quantum consistency)

Any quantum-enabled information/computation claim must state:

- state prep assumptions,
- measurement model,
- decoherence/error assumptions,
- no-communication/no-signaling compliance.

### Marker P3 (thermodynamic budget)

Claims of persistent storage/compute/transmission in astrophysical media require explicit energy dissipation or lower-bound accounting assumptions.

---

## 6) Provability classes for automation gating

To support automated repo improvement, every proposed change receives a **proof profile**:

- `F-proof`: theorem/derivation check (symbolic consistency).
- `C-proof`: program/model invariant or static/dynamic proof artifact.
- `E-proof`: experiment/simulation with reproducible protocol and statistical result.

### Gate policy

- **Auto-merge eligible:** at least one strong proof profile + no violated hard constraint markers.
- **Human review required:** mixed evidence, weak confidence, or cross-domain ontology extension.
- **Reject/rollback:** any violation of C1/I1/P1/P2 or unverifiable objective claims.

---

## 7) Criterion markers (canonical set)

Use these stable IDs in code, tests, and docs.

### Ontological markers

- **O1** Ontology adequacy
- **O2** Explicit semantics for every new symbol
- **O3** Non-metaphorical mapping (concept ↔ measurable/stateful construct)

### Temporal-observer markers

- **N1** Bounded-now access (no latency-free global present oracle)
- **N2** Measurement-backaction acknowledgment/modeling
- **N3** Causal-admissible prediction/retrodiction framing

### Information markers

- **I1** Capacity admissibility
- **I2** Forecasting information gain over baseline
- **I3** Error-bound declaration and validation

### Computational markers

- **C1** Forward-causal admissibility
- **C2** Resource-bounded loop operation
- **C3** Termination/stability guarantee
- **C4** Semantic-preservation under change

### Physical markers

- **P1** Relativistic consistency
- **P2** Quantum consistency/no-signaling compliance
- **P3** Thermodynamic/energy accounting

### Empirical prediction markers

- **E1** Pre-registration integrity (timestamped, locked before observation)
- **E2** Proper scoring rule declaration (e.g., Brier/log/RMSE) and pass threshold
- **E3** Calibration quality tracked over rolling windows
- **E4** Predictive lift vs declared baseline
- **E5** Novelty criterion (non-trivial vs baseline heuristic)

### Operational markers

- **A1** Reproducibility (script + seed + config)
- **A2** Traceability (claim ↔ file ↔ test ↔ evidence)
- **A3** Rollback safety and audit trail

---

## 8) Theory tiering policy (for “astral computing”)

Every statement in this domain must carry one tier tag:

1. **Tier-1 Established:** consistent with accepted physics + information/computation theory.
2. **Tier-2 Plausible extrapolation:** explicit assumptions, partially constrained by known theory.
3. **Tier-3 Speculative frontier:** exploratory, no deployment-level commitment.

Automation behavior:

- Tier-1/Tier-2 can enter experimental implementation with markers.
- Tier-3 cannot drive autonomous policy promotion without human approval.

---

## 9) Automation-cycle contract (proposal → retention)

Every autonomous improvement cycle must execute:

1. **Propose** change with claim labels (F/C/E/S) and target markers.
2. **Implement** with minimal diff and explicit affected contracts.
3. **Evaluate** via marker-linked tests/experiments.
4. **Decide** using gate policy (auto-merge / human review / rollback).
5. **Record** evidence artifact for traceability.

### Minimum evidence payload (required)

- claim ID(s),
- marker ID(s),
- changed files,
- validation commands + outputs,
- decision + rationale,
- rollback plan/result,
- branch/lane identifier (when applicable),
- disposition or promotion target,
- spine linkage (`concept_id`, `pressure_event_id`, and/or `promotion_event_id`) when the work materially affects a tracked concept.

### Branch continuity discipline

For any non-trivial branch run (implementation, research, automation, or policy-affecting analysis), the cycle must end with an explicit disposition.

Recommended disposition classes:

- `DROP_LOCAL`
- `LOG_ONLY`
- `TODO_PROMOTE`
- `DOC_PROMOTE`
- `POLICY_PROMOTE`
- `ESCALATE`

Silent termination is admissible only for discarded scratch work with no claimed evidence, no external effect, and no requested follow-on consequence.

### Promotion admissibility

Promotion into more durable surfaces (`docs/`, `WORKFLOW.md`, `FOUNDATIONS.md`, tests/config, or equivalent policy-bearing artifacts) requires:

- explicit provenance,
- an evidence-bearing rationale proportionate to consequence,
- and a rollback or reversal path when practical.

### Spine governance rule

When a concept becomes important enough to influence architecture, canonical docs, automation policy, or cross-surface continuity, it should no longer live only as scattered prose.

At that point it should be represented in the repo spine with:
- a **concept node** (`spine/concepts/*.yaml`)
- at least one **pressure** or **promotion** record when a meaningful evaluation or state transition occurs

This is the project's lightweight mechanism for keeping concept evolution inspectable.

---

## 10) Non-negotiable prohibitions

The following are never admissible in project-facing claims or automation behavior:

1. Claims implying backward-time operational signaling without explicit causal-compatible reduction.
2. Claims exceeding channel/compute/energy limits without declared assumptions.
3. Metaphorical language presented as verified mechanism.
4. Policy promotion from speculative claims without empirical/computational support.
5. Claims assuming latency-free direct access to a universal "real now" without explicit observer/frame/latency model.

---

## 11) Short implementation checklist

Before accepting any non-trivial change:

- [ ] Claims labeled (F/C/E/S)
- [ ] At least one criterion marker satisfied and evidenced
- [ ] No hard-marker violations (C1/I1/P1/P2)
- [ ] If time/observer coupling is involved, N1/N2/N3 constraints are explicitly addressed
- [ ] Theory-implementation matrix row updated
- [ ] Explicit branch disposition/promotion target recorded when applicable
- [ ] Reproducibility + rollback artifacts stored

---

## 12) Relationship to existing docs

- `docs/01_foundations.md` explains conceptual basis and causal framing.
- This `FOUNDATIONS.md` is the **formal governance contract** for automation and implementation rigor.
- `docs/theory-implementation-matrix.md` is the operational traceability ledger.
- `spine/README.md` defines the concept / pressure / promotion spine for repo-level intellectual state tracking.
