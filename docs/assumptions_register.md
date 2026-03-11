# Assumptions Register

Purpose: maintain a **single explicit ledger of assumptions** used across Sandy Chaos.

This document is not a proof and not a replacement for the canonical theory docs. Its job is narrower and more practical:

- separate **derived results** from **adopted assumptions**,
- show **what each assumption enables**,
- show **what depends on it**,
- and make the consequences of weakening or rejecting an assumption legible.

If `FOUNDATIONS.md` is the hard contract and `theory-implementation-matrix.md` is the claim ledger, this file is the **dependency map** between them.

---

## 1) How to use this register

When adding or revising a nontrivial claim, ask:

1. **What is being assumed?**
2. **What kind of assumption is it?**
3. **Where is it used?**
4. **What does it enable?**
5. **What breaks, narrows, or gets quarantined if it fails?**
6. **What markers or tests should constrain it?**

If a claim depends on an assumption that is only `Open` or `Speculative`, that claim should not be presented as stronger than that dependency chain permits.

---

## 2) Assumption kinds

Use one or more of these labels per row:

- **Formal / Math** — number systems, manifolds, analytic machinery, abstract state constructions.
- **Physical** — relativity, causal ordering, no-signaling, thermodynamic constraints.
- **Modeling** — framework-specific mappings and abstractions used to make the problem tractable.
- **Computational** — implementation choices, schemas, metrics, discretizations, or software contracts.
- **Governance** — claim-tiering, marker policies, audit rules, promotion gates.
- **Speculative** — interpretive or forward-looking assumptions not yet justified strongly enough for operational reliance.

These are assumption labels, not claim tiers. A claim may be empirical while still relying on modeling or physical assumptions.

---

## 3) Status labels

- **Contract** — hard project boundary; changing it would redefine Sandy Chaos.
- **Adopted** — currently accepted working assumption.
- **Implemented** — concretely represented in code/docs/protocol surfaces.
- **Partial** — some implementation or test support exists, but not enough to close the loop.
- **Open** — actively relied on conceptually, but not yet validated or narrowed sufficiently.
- **Speculative** — exploratory only; cannot carry strong operational conclusions.

---

## 4) Consequence classes

If an assumption is challenged, classify the impact:

- **Collapse** — the current framing fails at the core and must be redefined.
- **Downscope** — the project survives, but claims must narrow substantially.
- **Redirect** — replace the mechanism with a weaker or alternative one.
- **Quarantine** — move the affected layer into explicitly speculative territory.

---

## 5) Register

| ID | Assumption | Kind | Status | Primary surfaces | What it enables | If weakened or false | Consequence | Marker / matrix links |
|---|---|---|---|---|---|---|---|---|
| A-001 | **No ontic backward-causal channel is permitted.** Present state cannot operationally depend on future intervention. | Physical, Governance | Contract | `FOUNDATIONS.md`, `docs/01_foundations.md`, `docs/02_tempo_tracer_protocol.md` | Defines the repo’s core identity: future-like effects must remain forward-causal. | Sandy Chaos, as currently defined, stops being itself; retrocausal interpretations would no longer be excluded. | Collapse | C1, P1; T-001, T-002, T-010 |
| A-002 | **Future-like informational advantage must reduce to timing asymmetry + inference + lawful structural propagation.** | Physical, Modeling | Adopted | `docs/01_foundations.md`, `docs/02_tempo_tracer_protocol.md`, `docs/math_appendix.md` | Preserves a causal explanation for forecasting advantage without superluminal claims. | Central explanatory language must downshift to ordinary forecasting/latency effects or another explicit mechanism. | Downscope | C1, I2, P1; T-002 |
| A-003 | **Boundary-propagation / upstream-legibility models are an admissible explanatory scaffold for epistemic retro-influence.** | Modeling | Adopted, Open | `docs/01_foundations.md`, `docs/05_hyperstition_temporal_bridge_analysis.md`, `docs/math_appendix.md` | Gives the project a physical-looking way to discuss downstream structure becoming locally legible upstream. | Retain causality discipline but replace this scaffold with a weaker or more domain-specific forward model. | Redirect | O3, C1; T-002 |
| A-004 | **Proper-time asymmetry is an operationally relevant observable for directional communication metrics.** | Physical, Empirical | Adopted, Open | `docs/02_tempo_tracer_protocol.md`, `docs/05_hyperstition_temporal_bridge_analysis.md`, channel metrics docs/code | Supports directional capacity surfaces and lead/lag-budget language. | The project can still study asynchronous observers, but relativistic distinctiveness weakens. | Downscope | P1, I2, E4; T-002 |
| A-005 | **Kerr / curved-spacetime structure contributes something theoretically load-bearing beyond generic flat-space timing asymmetry.** | Physical, Modeling | Open | `docs/02_tempo_tracer_protocol.md`, `docs/math_foundations_zf.md` | Justifies why curved geometry is more than aesthetic packaging. | Treat Kerr as an illustrative or special-case model only; do not market curvature as essential until stronger evidence exists. | Downscope | P1, O3; T-005 |
| A-006 | **The complex entropy state** $Z = \alpha + i\beta$ **is a useful canonical embedding for the order/disorder state space.** | Formal / Math, Modeling | Adopted, Partial | `docs/math_foundations_zf.md`, `docs/math_appendix.md`, duality-space code | Enables magnitude/phase language, winding diagnostics, and a compact state representation. | Replace with a real vector/two-channel representation; keep the phenomena if they survive without complex notation. | Redirect | O2, O3, C4 |
| A-007 | **Entropic circulation / winding diagnostics detect topological structure, not tachyonic behavior.** | Modeling, Computational | Adopted, Implemented | `nfem_suite/main.py`, `nfem_suite/simulation/temporal/tachyonic_loop.py`, `docs/math_foundations_zf.md` | Preserves the useful contour/winding machinery while removing a misleading physical interpretation. | Quarantine the feature or rename/reframe again if it still implies unsupported physics. | Quarantine | O3, C4 |
| A-008 | **Narrative / hyperstitional variables operate at the policy, interpretation, or boundary-conditioning layer—not as law-violating forces.** | Modeling, Governance | Adopted, Open | `docs/05_hyperstition_temporal_bridge_analysis.md`, `docs/06_observer_ouroboros.md` | Allows narrative to matter without pretending it overrides physics. | Keep hyperstition as interpretive language only, or quarantine it until a bounded operational model exists. | Quarantine | O3, C1, A2; T-012 |
| A-009 | **Observer read-write coupling is measurable as perturbation induced by measurement policy, feedback, or interaction structure.** | Modeling, Computational, Empirical | Partial | `docs/03_micro_observer_agency.md`, `docs/06_observer_ouroboros.md`, observer-coupling code | Grounds agency/observer effects in measurable mismatch or perturbation rather than metaphor. | Downscope to passive observation + control heuristics until domain-specific measurement/write-back effects are specified. | Redirect | O3, E2, C4 |
| A-010 | **The minimal temporal packet schema** $P_{min}=\{payload,\tau_{send},\sigma_{send},confidence,checksum\}$ **is the current implementation contract.** | Computational | Implemented | `docs/02_tempo_tracer_protocol.md`, `docs/math_appendix.md`, `nfem_suite/simulation/communication/temporal_protocol.py` | Keeps docs honest about what exists now; audit metadata becomes an explicit extension rather than implied reality. | Either enrich the implementation or keep all richer packet claims marked experimental/planned. | Redirect | A2, C4 |
| A-011 | **Claim tiers + marker gates meaningfully constrain repo drift.** | Governance | Adopted, Partial | `FOUNDATIONS.md`, `docs/README.md`, `docs/theory-implementation-matrix.md` | Lets the repo distinguish defensible, open, and speculative layers instead of letting them blur together. | Documentation and automation drift back toward overclaiming; stronger linting/tests become necessary. | Redirect | O1, A2, A3; T-003, T-007 |
| A-012 | **Empirical success requires lift over declared baselines with reproducible metrics.** | Empirical, Governance | Adopted, Open | `docs/prediction-protocol.md`, `docs/09_research_automation_protocol.md`, `docs/theory-implementation-matrix.md` | Gives the project a scientific success criterion rather than a vibes-based one. | Predictions and demos become illustrative only; no strong framework-success claim should be made. | Downscope | E1–E5, I2, A1 |
| A-013 | **Speculative design layers (e.g. axiomatic injection, potential-flow contract proposals; legacy geodesic-hydrology / geometric-transport phrasing) must remain sandboxed until they cash out in explicit models/tests.** | Governance, Speculative | Contract, Adopted | `docs/06_observer_ouroboros.md`, `docs/11_geodesic_hydrology_contracts.md`, `FOUNDATIONS.md` | Preserves ambition without letting speculative language silently become policy or “fact.” | These layers can remain in the repo, but only as roadmap/proposal material with visible labels. | Quarantine | O3, A2; T-007, T-011 |

---

## 6) How to reason about consequences

A useful way to read the table is:

- **A-001 fails** → the framework’s identity collapses.
- **A-005 fails** → the framework survives, but curved-spacetime specificity must be downscoped.
- **A-006 fails** → the representation changes, but not necessarily the underlying phenomena.
- **A-008 fails** → hyperstition becomes interpretation/UX language rather than theoretical machinery.
- **A-010 fails** → docs or code must be corrected immediately; this is a documentation-truth problem, not a metaphysical one.

This lets the project distinguish between:

- assumptions that are **load-bearing**,
- assumptions that are **replaceable modeling conveniences**,
- and assumptions that are **interesting but quarantinable**.

---

## 7) Maintenance rules

1. **Every new major theory doc** should either:
   - cite relevant assumption IDs directly, or
   - introduce new assumption rows here.
2. **If an assumption status changes**, update:
   - this register,
   - the relevant canonical docs,
   - and any impacted rows in `docs/theory-implementation-matrix.md`.
3. **If a claim depends on an `Open` or `Speculative` assumption**, the claim should not be promoted above that support level.
4. **If a row is tagged `Collapse`**, changing it requires explicit human review.
5. **If a row is tagged `Quarantine`**, the burden is on the author to keep it visibly separated from operational claims.

---

## 8) Immediate next uses

This register should help with at least four near-term tasks:

1. **Audit canonical docs for hidden dependencies**
   - especially where a claim sounds derived but actually rests on modeling choice.
2. **Improve theory-to-implementation traceability**
   - especially for `T-005`, `T-007`, `T-011`, and `T-012` in the theory-implementation matrix.
3. **Clarify what can be tested next**
   - by focusing on assumptions currently labeled `Open` or `Partial`.
4. **Reason about fallback positions**
   - e.g. what Sandy Chaos still is if Kerr-specific leverage or hyperstition-specific machinery weakens.

This should remain a living document. A short, honest register that gets updated is more valuable than a grand perfect register that freezes and rots.
