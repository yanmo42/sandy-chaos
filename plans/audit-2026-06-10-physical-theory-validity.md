# Physical Theory Validity Audit — 2026-06-10

**Type:** external-style adversarial audit (full-repo read, line-level evidence)
**Scope:** core mechanism (A-002/A-003), Kerr layer (A-004/A-005, T-015), complex entropy state (A-006, T-016), hyperstition (A-008, T-012), assumptions register, proof-path positioning, automation gates.
**Status:** findings logged; remediation backlog below is the actionable surface.
**Claim discipline:** every finding below is tiered and cites file:line evidence. Nothing here is a vibe.

---

## 0) Headline

- The governance stack (FOUNDATIONS contract + assumptions register + proof-path ladder) is **defensible now** and above-median for an independent research program.
- The hyperstition toy lane (T-012) is a **genuine internal Level-4 result** with correct discipline (null + ablation + robustness + pre-declared failure envelope).
- The repo's **only physics PASS (T-015) does not survive audit** and is contaminating downstream prose.
- The core-mechanism's validated artifact tests a **different PDE class** (parabolic/Péclet) than the stated mechanism (hyperbolic/Froude), and never tests a *temporally future* target — so the "future-like advantage" name-claim is currently at proof-path **Level 2**, not Level 4.
- Honest program position on the ladder: **Level 3 overall**, one true L4 surface (hyperstition), one unsound L4 claim (Kerr).

---

## 1) Findings register (problems to fix)

Severity: **S1** = contaminates ledger/policy surfaces now; **S2** = blocks the central claim from advancing; **S3** = correctness/hygiene debt.

### AUD-001 (S1) — T-015 PASS is unsound; measured quantity is not proper time
- **Surface:** `docs/theory-implementation-matrix.md` row T-015; `research/kerr_asymmetry_validation.py`; `cosmic_comm/physics/geodesics.py`
- **Evidence:**
  - Validation traces **null** geodesics (`kerr_asymmetry_validation.py:36–44` enforces `g^μν p_μ p_ν = 0`; `geodesics.py:4` "photon paths (null geodesics)"). Proper time along a null geodesic is identically zero.
  - Reported "proper_time" is `len(ts) * self.dt` (`geodesics.py:98`) — elapsed **affine parameter**, gauge-dependent (E=1 normalization, step size 0.05, capture margin 1.05).
  - Flat-space comparator (`kerr_asymmetry_validation.py:85–113`) produces only **negative** asymmetries (−0.01 … −1.36) vs all-positive Kerr values, so "best-fit flat match" is always the v=0.1 strawman and the relative residual is trivially ≈100%+. **The test cannot fail.**
  - Criterion conflation: at a/M=0.1, asymmetry = 2.28% and absolute residual = 3.3% (`memory/research/kerr_asymmetry_2026-03/validation_results.json`), both below the stated 5% bar; PASS rides on the meaningless relative residual.
  - The correct mundane comparator (Sagnac asymmetry in a rotating flat frame) was never run; the Kretschmann-invariant argument (`docs/math_foundations_zf.md:388–390`, also misspelled "Kretschner") shows curvature invariance, not channel-observable unmimickability.
- **Required fix:** demote T-015 to REVIEW immediately (evidence-payload update per matrix schema). Rebuild with (a) timelike orbits + actual ∫dτ, or an invariant null observable (distant-observer round-trip coordinate-time asymmetry); (b) Sagnac rotating-frame flat baseline; (c) the **spin-dependence curve** as the discriminating object, not a scalar.
- **Markers:** P1, E4, A2. **Matrix:** T-015. **Register:** A-004, A-005.

### AUD-002 (S1) — T-015 contamination has propagated into canonical prose
- **Surface:** `docs/math_foundations_zf.md` §9 ("Empirical validation (2026-03-30) … confirms"), `plans/todo.md:181` ("proves it's not removable by boost"), matrix High-confidence cell.
- **Required fix:** annotate/retract those statements pending AUD-001 rebuild. This is the repo's first observed instance of the laundering failure mode it was designed to prevent — record it as a governance lesson (spine pressure event on the relevant concept).
- **Markers:** A2, O3.

### AUD-003 (S2) — Mechanism mismatch: validated artifact is parabolic (Pe), stated mechanism is hyperbolic (Fr)
- **Surface:** `docs/01_foundations.md:77–88` (Fr < 1, finite `c_up = √(gh) − u`, finite delay τ_u > 0) vs `research/subcritical_information_demo.py:20–29` (Péclet-controlled advection-diffusion).
- **Evidence:** parabolic PDEs propagate influence at infinite speed (exponentially damped). The theory's signature "finite positive delay, no instantaneous channel" claim is **not realized** by the artifact cited as its first demonstration. The demo is correct mathematics demonstrating textbook diffusion legibility — it does not discriminate the stated wave mechanism.
- **Required fix:** implement the shallow-water / hyperbolic version where upstream influence genuinely travels at finite `c_up`, and verify the measured onset delay matches τ_u = (L−x_u)/c_up.
- **Markers:** O3, C1, I2, E5. **Matrix:** T-002. **Register:** A-002, A-003, new H-4 (below).

### AUD-004 (S2) — "Future-like advantage" never tests a temporally future target
- **Surface:** `research/subcritical_information_demo.py` (target is B, the current/past boundary state); all "anticipatory" language in docs/00–02.
- **Evidence:** measured MI is spatial legibility `I(q(x_obs); B)`. No artifact maps "downstream in space" → "future in time." I2 as defined (`FOUNDATIONS.md:107–113`) requires ΔI over a baseline observation set; the demo's null is channel-off, not best-inference-without-method.
- **Required fix:** moving-observer experiment — observer advected toward the boundary; target = observer's own local state at t+τ; baselines = (i) matched observer with the upstream channel removed, (ii) history-only autoregressive forecaster. Pre-register lead-time-vs-regime predictions.
- **Markers:** I2, E1, E4, E5. **Matrix:** T-002. **Register:** A-002 + new H-1.

### AUD-005 (S2) — §11 math error: arc-length integral conflated with complex contour integral
- **Surface:** `docs/math_foundations_zf.md:443–476` (§11).
- **Evidence:** τ_γ is defined as ∫ Z(s)‖dγ/ds‖ds (arc-length). Cauchy's theorem applies to ∮ f(z) dz, **not** ∮ f |dz|. With α,β ∈ [0,1] ≥ 0, Re ∮ Z |dz| ≥ 0 and is nonzero for any generic field regardless of singularities — so "ΔT ≠ 0 ⟺ enclosed defect" is false under the stated definition. The winding-number formula uses the (different, correct) dz integral. Also: a curve confined to [0,1]² can never wind around 0; winding around interior z₀ is z₀-dependent (modeling choice, not invariant).
- **Required fix:** either redefine τ_γ as ∮ Z dz (Cauchy applies; Re/Im order/disorder reading breaks) or keep arc-length and delete the Cauchy/singularity diagnostic. Update `complex_euler.py` docstrings to match. Then run the A-006 ablation: re-express one downstream result in plain (α,β) ∈ ℝ² and record what, if anything, is lost.
- **Markers:** O2, O3, C4. **Matrix:** T-016 (adjacent). **Register:** A-006, A-007.

### AUD-006 (S2) — Kerr layer is structurally disconnected from the information-theoretic code
- **Surface:** `nfem_suite/` (no Kerr import anywhere); `nfem_suite/simulation/communication/vortex_channel.py:36` (asymmetry = hand-set scalar `backward_attenuation: float = 0.5`).
- **Evidence:** nothing downstream consumes T-015 outputs except prose. "Load-bearing" requires a downstream claim whose truth/measured value changes under Kerr-specific structure vs a generic asymmetric-delay channel. No such consumer exists.
- **Required fix:** either wire a Kerr-derived asymmetry profile into `VortexChannel` (replacing the hand-set scalar) and show a metric that distinguishes it from generic attenuation — or execute A-005's downscope now ("Kerr as illustrative only") and say so in `docs/02` and `math_foundations_zf.md` §9.
- **Markers:** O3, P1. **Register:** A-004, A-005.

### AUD-007 (S2) — Narrative–boundary coupling exists in docs, not in code
- **Surface:** `docs/05_hyperstition_temporal_bridge_analysis.md:47–50` (`q(L,t) = B₀(t) + λN_t`) — never implemented. The toy model's "temporal asymmetry Δ" is a constant additive bias (`nfem_suite/intelligence/cognition/hyperstition.py:86–87`); nothing temporal occurs in the dynamics.
- **Required fix:** implement the q-coupling so narrative conditions a simulated medium's boundary; test whether the corridor structure (Level-4 packet) survives when narrative acts through the medium rather than directly through the action channel. This is the single cheapest move that connects the repo's two best surfaces.
- **Markers:** O3, C1, A2. **Matrix:** T-012 extension. **Register:** A-008, A-009.

### AUD-008 (S1) — Hard-gate enforcement is an honor system
- **Surface:** `scripts/validate_foundations.py:86–96` (`_extract_explicit_violation_markers`): C1/I1/P1/P2 failures trigger only when the payload **self-declares** them. `scripts/self_improve.py:505` promotes policy tweaks on a frequency gate (min_count=3) plus contract check, with no evidence-quality re-derivation.
- **Required fix:** any matrix-row transition to PASS must require an adversarial verifier pass that (a) re-derives the claimed observable from the code and (b) audits comparator adequacy (see AUD-009). Artifact-existence is not evidence-adequacy.
- **Markers:** A2, A3, C4. **Matrix:** T-003, T-006, T-007.

### AUD-009 (S2) — Recurring failure mode: weak comparator classes ("strawman baselines")
- **Evidence:** T-015 tested against a sign-mismatched boost family instead of Sagnac; subcritical demo tested against channel-off instead of a history-based forecaster; pre-registration in `subcritical_information_demo.py:34–43` lives in the same script that evaluates it (weak E1) and the predictions follow analytically from the model's own closed form (E5 novelty fails).
- **Required fix:** adopt a standing rule — no Level-4 status without naming and implementing the **strongest known causal-mundane mechanism** that produces the same observable, as the baseline. Proposed spine node: `SC-CONCEPT-0010: strongest-mundane-comparator`.
- **Markers:** E1, E4, E5, A2.

### AUD-010 (S3) — Hidden load-bearing assumptions missing from the register
Add rows to `docs/assumptions_register.md`:
- **H-1:** "downstream in space" ↔ "future in time" mapping exists for some observer class (every "future-like" claim depends on it; untested).
- **H-2:** affine-parameter differences along null geodesics proxy proper-time/channel timing (assumed by T-015; false as stated).
- **H-3:** comparator classes in discriminating tests contain the strongest mundane alternative (violated twice).
- **H-4:** parabolic diffusion adequately stands in for the finite-`c_up` hyperbolic mechanism, including finite delay (currently false in the validated artifact).
- **H-5:** MI about a boundary implies decision-relevant anticipatory advantage (needs I2 baseline form).
- **H-6:** automation gate honesty — hard-gate enforcement assumes proposers declare their own violations.
Also consider: relabel **A-012** consequence from Downscope toward Collapse-for-the-science (program identity is effectively A-001 ∧ A-002 ∧ eventual A-012), and note that A-002's fallback ("ordinary forecasting/latency effects") currently describes the actual evidential state.

### AUD-011 (S3) — Honest proof-path placement (correct the implicit ledger)
| Surface | Implied | Honest | Note |
|---|---|---|---|
| Subcritical core (T-002) | L4 | **L3** | artifact real; test confirms textbook physics, not the mechanism claim |
| "Future-like advantage" framing | — | **L2** | no artifact targets a future observable |
| Kerr (T-015) | L4 PASS | **L3** | discriminating test fails L4 entry conditions |
| ZF→ℚ chain (T-016) | L3 | **L3 (terminal)** | infrastructure; cannot climb, by design |
| Hyperstition toy (T-012) | L4 | **L4 (internal)** | genuine; packet correctly refuses L5 |
| Tempo Tracer capacity / T-013 / T-014 / T-017 | L2–L3 | **L2** | validation columns all say "to add" |
| Narrative–boundary coupling | L3-ish prose | **L2** | equation written, never implemented |

### AUD-012 (S3) — Minor corrections
- "Kretschner" → **Kretschmann** (`docs/math_foundations_zf.md:388`).
- `plans/todo.md` resolution table rows #1, #2, #6 marked ✅ Resolved are contradicted by AUD-001/-002/-005; reopen with audit flags (do not rewrite history — annotate).

---

## 2) Recommended first step (single move, if only one is taken)

**Demote T-015 from PASS to REVIEW and rebuild the Kerr validation correctly** (AUD-001 + AUD-002):

1. Update the T-015 matrix row: Decision → REVIEW, gap column → cite this audit, confidence → Low. Attach an evidence payload per the matrix schema (`matrix_id`, `markers`, `result_summary`, `rollback_status`).
2. Annotate `docs/math_foundations_zf.md` §9 and `plans/todo.md:181` with a retraction-pending note.
3. Rebuild: timelike geodesics + ∫dτ (or invariant round-trip observable), Sagnac flat-frame baseline, spin-curve criterion, error bars across step sizes.

**Why this first, ahead of the more exciting moving-observer experiment (AUD-004):** a false PASS in the traceability ledger corrupts every downstream consumer of the ledger — including the automation loop, which trusts matrix status. Fixing the ledger is cheap (hours), unblocks honest prioritization, and demonstrates the governance system actually self-corrects, which is itself the program's most externally legible asset right now. The moving-observer experiment is the highest-leverage *new science* and should be move #2.

---

## 3) Agentic development backlog (bounded task contracts)

Ordered. Each contract is sized for one bounded lane pass with explicit disposition.

### Contract 1 — Ledger repair (AUD-001/-002/-012)
- **Goal:** T-015 → REVIEW; retraction-pending annotations in `math_foundations_zf.md` §9 and `plans/todo.md`; fix "Kretschmann".
- **Constraints:** no deletion of historical evidence artifacts; annotate, don't rewrite.
- **Done when:** matrix row updated with evidence payload; `python3 scripts/validate_foundations.py --payload-file <payload.json>` passes; spine pressure event recorded against the Kerr-adjacent concept.
- **Disposition:** DOC_PROMOTE.

### Contract 2 — Kerr validation rebuild (AUD-001)
- **Goal:** new `research/kerr_asymmetry_validation_v2.py` per §2 step 3.
- **Done when:** spin-curve result with Sagnac baseline, error bars, and a criterion that **can fail**; T-015 re-decided on the new evidence (PASS or FAIL both acceptable outcomes).
- **Failure condition (pre-registered):** if the Sagnac-matched baseline reproduces the spin curve within error, A-005 downscope executes immediately (Contract 6 short-circuits to the downscope branch).
- **Disposition:** TODO_PROMOTE → matrix row update.

### Contract 3 — Hyperbolic subcritical mechanism (AUD-003)
- **Goal:** shallow-water / linearized hyperbolic solver; verify upstream onset delay ≈ (L−x_u)/c_up; reproduce the MI-vs-regime transition in the wave regime.
- **Done when:** results JSON + plot in `memory/research/`, matrix T-002 row updated with the artifact, finite-delay claim either validated or corrected in `docs/01`.
- **Disposition:** DOC_PROMOTE.

### Contract 4 — Moving-observer anticipatory ΔI (AUD-004) — *the core-thesis test*
- **Goal:** observer advected toward boundary; target = its own future local state; baselines = channel-removed twin + history-only forecaster; ΔI per marker I2 with CIs.
- **Pre-registration:** lock predictions in a separate dated file **before** running (fixes the E1 weakness); declare pass/fail thresholds.
- **Done when:** one completed run either showing ΔI > 0 with lead time scaling as predicted, or a clean negative. Both are program progress.
- **Disposition:** ESCALATE to human review (this is the name-claim).

### Contract 5 — §11 math repair + A-006 ablation (AUD-005)
- **Goal:** fix the arc-length/contour conflation; choose one coherent definition; rerun the (α,β) ∈ ℝ² ablation on one downstream result.
- **Done when:** §11 internally consistent; ablation note states what the complex embedding buys (possibly: nothing — that is an acceptable, recordable answer per A-006's fallback).
- **Disposition:** DOC_PROMOTE.

### Contract 6 — Kerr↔channel wiring or downscope (AUD-006)
- **Goal:** branch on Contract 2 outcome. PASS branch: derive `backward_attenuation` profile from Kerr geometry and show a metric distinguishing it from a generic scalar. FAIL branch: execute A-005 downscope across `docs/02`, `math_foundations_zf.md` §9, register.
- **Disposition:** POLICY_PROMOTE (register status change) — human review required.

### Contract 7 — Narrative-boundary coupling implementation (AUD-007)
- **Goal:** implement `q(L,t) = B₀ + λN_t`; test corridor-structure survival through the medium.
- **Done when:** comparison artifact vs the existing Level-4 packet arms; failure envelope updated.
- **Disposition:** TODO_PROMOTE.

### Contract 8 — Verifier-lane hardening (AUD-008/-009)
- **Goal:** add to `scripts/validate_foundations.py` (or a sibling) a PASS-transition check requiring: comparator-class declaration, strongest-mundane-comparator statement, and independent re-derivation note. Add `spine/concepts/SC-CONCEPT-0010-strongest-mundane-comparator.yaml`.
- **Done when:** a synthetic payload claiming PASS without comparator declaration is rejected in tests.
- **Disposition:** POLICY_PROMOTE — human review required.

### Contract 9 — Register update (AUD-010)
- **Goal:** add H-1…H-6 rows; reconsider A-012 consequence class; cross-link to this audit.
- **Disposition:** DOC_PROMOTE.

---

## 4) What this audit explicitly does NOT claim

- It does not claim the Kerr qualitative physics is wrong — prograde/retrograde photon dynamics in Kerr genuinely differ (textbook). It claims the *validation as run* cannot support the load-bearing conclusion.
- It does not claim hyperstition is pseudoscience — the policy-layer framing is coherent and has mainstream ancestry (Merton, performativity, mean-field games). It claims the physics-flavored coupling is currently unimplemented.
- It does not claim the program is hollow — the governance machinery and the hyperstition lane are real assets. It claims the gap between the matrix's recorded state and the audited state is concentrated almost entirely in one PASS row, and that fixing the ledger is therefore unusually cheap relative to the credibility it buys.
