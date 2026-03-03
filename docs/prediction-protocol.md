# Prediction Protocol (Scientific Correctness + Novelty)

Purpose: define a rigorous, falsifiable process for making and scoring predictions inside Sandy Chaos so the framework produces **real scientific value** (not post-hoc narratives).

This protocol extends `FOUNDATIONS.md` and is enforced through matrix rows in `docs/theory-implementation-matrix.md`.

---

## 1) Prediction object model

A prediction is valid only if it is represented as a structured object with:

- `prediction_id`
- `hypothesis_id`
- `model_version` (commit hash)
- `claim_class` (typically E, sometimes C+E)
- `tier` (Tier-1/2/3)
- `target_variable`
- `prediction_time`
- `observation_time_window`
- `allowed_inputs_cutoff`
- `predicted_distribution` or `predicted_interval`
- `confidence_statement`
- `baseline_models`
- `scoring_rule`
- `pass_criteria`
- `markers` (at least E1, E2; often E3/E4/E5)

If any field is missing, prediction is `INVALID`.

---

## 2) Non-negotiable sequence

All predictions follow this lifecycle:

1. **Hypothesis** (state mechanism and assumptions)
2. **Pre-register** (lock object before outcome is known)
3. **Predict** (emit quantitative output)
4. **Lock** (immutable record + hash)
5. **Observe** (collect outcome)
6. **Score** (using predeclared rule)
7. **Update** (model/docs based on result)

No edits to predicted values are allowed after lock.

---

## 3) Marker requirements for predictive claims

### Required

- **E1** Pre-registration integrity
- **E2** Proper scoring rule declaration + threshold
- **A1** Reproducibility (script/config/seed)
- **A2** Traceability to files/tests/evidence

### Strongly recommended

- **E3** Calibration tracking (rolling reliability)
- **E4** Lift over baseline
- **E5** Novelty criterion

### Hard-fail conditions

A predictive claim is automatically `FAIL` if:

- prediction was not pre-registered before observation (`E1` fail),
- scoring rule was changed post-outcome (`E2` fail),
- baseline not declared when claiming advantage (`E4` fail),
- hidden future information leaked into inputs (`C1`/`E1` fail).

---

## 4) Scoring policy

Use proper scoring rules based on output type:

- **Binary events:** Brier score, log loss
- **Probabilistic multiclass:** log score / cross-entropy
- **Continuous quantities:** RMSE/MAE + interval coverage
- **Ranked outcomes:** NDCG / rank correlation

A prediction run is successful only if:

1. Correctness criterion met (score beats baseline by predefined margin), and
2. Calibration criterion not degraded beyond tolerance.

---

## 5) Novelty policy (anti-triviality)

A prediction counts as **novel** only when it beats non-trivial baselines and is not explainable by simple persistence/trend heuristics.

Minimum novelty checks:

- Compare against at least one naive baseline and one informed baseline.
- Report feature/assumption contribution analysis.
- Flag "novelty inflation" when lift is due to leakage or hindsight selection.

Use marker **E5** for novelty approval.

---

## 6) Uncertainty decomposition

Every prediction report must separate:

- **Aleatoric uncertainty** (irreducible noise)
- **Epistemic uncertainty** (model ignorance)
- **Assumption uncertainty** (Tier-2/Tier-3 dependence)

If assumption uncertainty dominates, claims cannot be promoted to governance policy without human review.

---

## 7) Paradox stress integration

Predictions that target informational/causal paradox scenarios must link a paradox case ID from `docs/paradox-registry.md`.

Required additions for paradox-linked predictions:

- explicit statement of apparent paradox,
- causal reduction expected by framework,
- contradiction trigger condition,
- marker stress set (typically C1, I1, P1, P2).

---

## 8) Evidence artifact schema

Store per prediction under `memory/predictions/` (or equivalent):

```json
{
  "prediction_id": "...",
  "timestamp": "...",
  "commit": "...",
  "paradox_case": "optional",
  "markers": ["E1", "E2", "A1", "A2"],
  "input_cutoff": "...",
  "prediction": {"type": "distribution", "value": "..."},
  "baseline": [{"name": "...", "score": 0.0}],
  "observed_outcome": "...",
  "scores": {"primary": 0.0, "baseline_delta": 0.0},
  "calibration": {"ece": 0.0},
  "decision": "PASS|REVIEW|FAIL",
  "notes": "..."
}
```

---

## 9) Promotion policy

- **PASS:** correctness + novelty + calibration satisfied.
- **REVIEW:** mixed results, weak significance, or heavy Tier-2/3 assumptions.
- **FAIL:** protocol violation or no baseline lift.

Only repeated `PASS` outcomes can support automation policy promotion.

---

## 10) Minimal immediate implementation checklist

- [ ] Add prediction artifact folder and schema validator.
- [ ] Add baseline library for core targets.
- [ ] Add scoring utility script.
- [ ] Add matrix rows for new prediction programs.
- [ ] Add CI check enforcing E1/E2 on prediction-tagged claims.
