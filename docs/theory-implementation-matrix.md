# Theory ↔ Implementation Matrix

Purpose: maintain bidirectional traceability between theoretical claims and concrete implementation artifacts.

This file is the operational ledger for rigorous automation. Each row must map:

- claim → formal/computational expression,
- implementation surface,
- validation evidence,
- decision gate status.

Canonical criteria markers are defined in `FOUNDATIONS.md`.

---

## How to use this matrix

1. Add or update a row whenever a theory-relevant change is proposed.
2. Reference marker IDs (O/I/C/P/E/A).
3. Link validation command(s) and evidence artifact(s).
4. Set decision status:
   - `PASS` (eligible)
   - `REVIEW` (human required)
   - `FAIL` (rollback/reject)

---

## Matrix

| ID | Theoretical claim | Claim class (F/C/E/S) | Formal / computational criterion | Marker(s) | Implementation surface | Validation command(s) | Evidence artifact | Gap / risk | Confidence | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| T-001 | System updates are forward-causal; no operational retrocausal dependency | F,C | `P(x_t | do(a_{t+Δ}), I_t) = P(x_t | I_t)` | C1, O2 | `docs/01_foundations.md`; loop policy in `docs/07_agentic_automation_loop.md` | `pytest -q` (causal tests as added) | `tests/` outputs + cycle logs | Need explicit automated causal invariant test suite if absent | Med | REVIEW |
| T-002 | "Future-like" advantage is attributable to inference + structural propagation, not superluminal signaling | F,E | Information gain over baseline `ΔI > 0` under causal constraints | I2, C1, P1 | `docs/01_foundations.md`, `docs/math_appendix.md`, simulation modules | simulation benchmark command (to be standardized) | benchmark report file | Benchmark protocol not yet standardized in one script | Low | REVIEW |
| T-003 | Agentic automation improves repo state while preserving theoretical constraints | C,E | Multi-objective gate: quality increase with no hard-marker violation | C2, C3, C4, A2, A3 | `scripts/self_improve.py`, `scripts/automation_orchestrator.py`, `scripts/orchestrator_autospawn.py`, `scripts/validate_foundations.py`, `docs/07_agentic_automation_loop.md` | `python3 scripts/self_improve.py full-pass --dry-run --foundations-evidence <payload.json>` | `memory/self_improve_state.json`, dispatch logs, validator summary | Foundational evidence gate now exists, but only for explicitly supplied payloads; broader cycle coverage still missing | Med | REVIEW |
| T-004 | Throughput/iteration gains must be resource-bounded and stable | C | `E[T_cycle] ≤ T_max`, bounded retries/watchdog | C2, C3 | scheduler + orchestrator scripts; systemd timer config | current ops validation command set | timer logs / dispatch logs | Resource envelope thresholds not centrally declared | Med | REVIEW |
| T-005 | Astral/astrophysical compute claims must be physically admissible | F,E,S | Must satisfy relativistic ordering + quantum no-signaling + energy accounting assumptions | P1, P2, P3, O3 | conceptual docs (`docs/01..06`, `docs/math_*`) and future models | domain-specific model checks (TBD) | `docs/assumptions_register.md` | Assumptions registry drafted; dedicated test harness still missing | Low | REVIEW |
| T-006 | Every promoted policy tweak must be reproducible and auditable | C | reproducibility payload + rollback path present | A1, A2, A3 | `scripts/self_improve.py`, `scripts/validate_foundations.py`; memory artifacts | `python3 scripts/validate_foundations.py --payload-file <payload.json>` | validator summary, `memory/notification_outbox.md`, state files | Evidence schema lint exists for matrix payloads; promotion-path coverage is still partial | Med | REVIEW |
| T-007 | Speculative claims cannot autonomously become governance policy | F,C | Tiered gating (Tier-1/2/3) with human approval for Tier-3 | O1, O3, A2 | `FOUNDATIONS.md` + governance docs | doc lint / policy check (to add) | policy audit note | No automatic enforcement yet in code | Low | REVIEW |
| T-008 | Scientific predictions must be pre-registered and scored with proper rules | E,C | Locked prediction object before observation; predeclared scoring rule + pass threshold | E1, E2, A1, A2 | `docs/prediction-protocol.md` | prediction schema validator + scoring script (to add) | `memory/predictions/*` | Protocol is documented but not yet tool-enforced | Med | REVIEW |
| T-009 | Predictive claims must show calibrated lift over baselines to count as framework success | E | `score_model - score_baseline > δ` with calibration tolerance | E3, E4, E5 | `docs/prediction-protocol.md`, benchmark harness (planned) | benchmark runner (to add) | prediction scorecards | Baseline library and novelty checks not yet implemented | Low | REVIEW |
| T-010 | Informational/causal paradoxes should be encoded as executable stress tests | F,C,E | Each paradox case has formal setup, falsifier, marker stress set, and prediction hook | C1, I1, P1, P2, E1, E2, A2 | `docs/paradox-registry.md`, planned `tests/paradox/` | paradox test harness (to add) | paradox case logs | Registry exists; executable tests still missing | Med | REVIEW |
| T-011 | Potential-flow contract proposals (legacy geodesic-hydrology / geometric-transport language) can reward path-quality dynamics without violating causal/physical constraints | C,E,S | Path-integral reward must improve baseline coordination metrics while preserving C1/I1/P1/P2 hard gates | C1, I1, P1, P2, O3, E2, E4, A2 | `docs/11_geodesic_hydrology_contracts.md`, future contract simulation harness | benchmark suite for anti-gaming/stability tests (to add) | proposal benchmark report (to add) | Currently conceptual; terminology clarified, but no contract simulator or benchmark evidence yet | Low | REVIEW |
| T-012 | Hyperstition narrative dynamics $\mathcal{G}$ are testable via a two-agent mean-field toy model with fixed-point classification | C,E | Fixed points satisfy $m^*=f(m^*)$ and stability by $|f'(m^*)|<1$; paradox regimes must be reproducible under bounded temporal asymmetry | C1, I1, E2, A2 | `nfem_suite/intelligence/cognition/hyperstition.py`, `docs/05_hyperstition_temporal_bridge_analysis.md` | `python -m unittest tests.test_hyperstition_dynamics -q` | `tests/test_hyperstition_dynamics.py` | Needs CI execution evidence in this environment | Med | REVIEW |
| T-013 | Operational-present axioms (N1 bounded-now, N2 measurement backaction, N3 causal-admissible retrodiction) can support reality-anchored prediction/reconstruction without violating causal constraints | F,C,E | Observation model includes explicit latency/policy terms and reconstruction claims remain consistent with C1: `y_i(τ_i)=M_i(x_{t-δ_i},π_i)+ε_i`, no dependence of present state on future intervention | N1, N2, N3, C1, I2, E2, A2 | `FOUNDATIONS.md`, `docs/00_sandy_chaos_blueprint.md`, `docs/02_tempo_tracer_protocol.md`, `docs/03_micro_observer_agency.md` | bounded-now / backaction / reconstruction benchmark harness (to add) | anchor/reconstruction benchmark report (to add) | No standardized now-contact metric or latency/backaction benchmark suite yet | Low | REVIEW |
| T-014 | Predictive processing across temporal frames can be modeled as neighbor-first graph-constrained message passing with potential-flow contract bounds, and should count only if it improves temporal coherence over simpler baselines without violating causal or physical gates | C,E,S | `score_contract_model - max(score_single_scale, score_unconstrained_multiframe) > δ` with bounded contract residuals, declared latency/distortion accounting, and no violation of C1/P1/P2 hard gates | C1, P1, P2, O3, E3, E4, A2 | `docs/16_temporal_predictive_processing.md`, `docs/11_geodesic_hydrology_contracts.md`, `docs/13_nested_temporal_domains.md`, future multiframe benchmark harness | temporal predictive-processing benchmark suite (to add) | temporal predictive-processing benchmark report + ablation table (to add) | Bridge architecture is now canonically specified, but no contract-bounded benchmark harness, residual implementation, or baseline comparison exists yet | Low | REVIEW |
| T-015 | Kerr geometry produces intrinsic proper-time asymmetry unattainable in flat spacetime, justifying the GR layer as load-bearing rather than aesthetic | F,E | Proper-time asymmetry `(τ_prograde - τ_retrograde) / mean(τ)` > 5% residual compared to best-fit flat-space model across spin parameters a/M ∈ [0.1, 0.9] | P1, P2, E3, E4 | `docs/math_foundations_zf.md` §9, `cosmic_comm/` simulation code, validation script | `python scripts/kerr_asymmetry_validation.py` | `memory/research/kerr_asymmetry_2026-03/validation_results.json`, `memory/research/kerr_asymmetry_2026-03/kerr_asymmetry_validation.png` | Validation complete: all spin values show >5% residual vs best flat-space match (0.1: 3.3%, 0.3: 7.8%, 0.5: 12.5%, 0.7: 17.5%, 0.9: 23.2%) | High | PASS |

---

## Hard-gate marker policy

The following marker violations are immediate `FAIL`:

- **C1** forward-causal admissibility violation
- **I1** capacity admissibility violation
- **P1** relativistic consistency violation
- **P2** quantum no-signaling/consistency violation

All other marker failures default to `REVIEW` unless explicitly configured as hard-gate in future policy.

---

## Required evidence schema (for any row update)

When changing a matrix row, include/update these fields in associated evidence artifact:

- `matrix_id`
- `claim_class`
- `markers`
- `files_changed`
- `validation_commands`
- `result_summary`
- `decision`
- `rollback_status`

---

## Near-term backlog to make this machine-enforceable

1. Expand `scripts/validate_foundations.py` beyond explicit payload checks into broader PR/task artifact coverage.
2. Add a standardized benchmark harness for information-gain deltas.
3. Expand and maintain the physics assumptions registry (`docs/assumptions_register.md`) for Tier-2/Tier-3 astral claims.
4. Gate `self_improve.py` policy promotion on matrix status and evidence schema completeness.
