# 22 Causal Leverage Card Protocol

> **Status:** operational protocol / matrix-row evidence harness.
>
> This document specifies the on-disk grammar and lifecycle for **causal leverage cards** — the artifact form of the closed-loop framing in `docs/21_closed_loop_causal_leverage.md`. Each card is the smallest reusable unit of evidence that takes a row in `docs/theory-implementation-matrix.md` from REVIEW toward PASS.
>
> Related docs:
>
> - `docs/21_closed_loop_causal_leverage.md` (concept)
> - `docs/theory-implementation-matrix.md` (matrix rows the cards feed)
> - `FOUNDATIONS.md` (marker semantics)
> - `spine/concepts/SC-CONCEPT-0010.yaml` (spine record)
>
> Claim posture:
>
> - **Defensible now:** declaring objective, baseline, denominators, risk vector, reversibility class, verification method, failure conditions, and measured outcome *before* deciding PASS/REVIEW/FAIL is a useful evidence discipline.
> - **Plausible but unproven:** the same card grammar can govern speculative substrate-control scenarios without becoming policy theatre.
> - **Speculative:** any single card retires a Sandy Chaos claim. Cards reduce ambiguity, but framework success is still measured across many cards and matrix rows.

---

## 1) What a card is for

A causal leverage card answers, for one bounded workflow:

> *Did this intervention move a declared metric over a declared baseline, with declared denominators and risk, in a way that survives the declared failure conditions?*

It exists to convert claims into matrix-row evidence under a uniform schema. The harness (`nfem_suite/intelligence/leverage/`) validates the card and emits a payload compatible with `scripts/validate_foundations.py`. The same payload feeds the matrix row's `validation_commands` and `evidence_artifact` columns.

Cards are not a substitute for tests, benchmarks, or proofs. They are a contract about *which* test, benchmark, or proof is being attested, on *what* denominator, with *what* reversibility, and what would have falsified the result.

## 2) Lifecycle

```
draft  →  prospective seal  →  measurement  →  scored card  →  matrix-row evidence  →  spine concept update
```

1. **Draft.** Author the card with `pre_registration.status = "prospective"` and every section populated *except* `measured_outcome`. Commit the draft. The commit hash goes into `pre_registration.card_seal_commit`.
2. **Measurement.** Run the workflow. Capture artifacts under `memory/research/leverage/` or another evidence directory referenced by `verification.evidence_artifacts`.
3. **Score.** Fill in `measured_outcome` and `decision`. Run `python scripts/run_leverage_card.py <card.json> --emit-evidence` to validate and emit `<card>.evidence.json`. Resolve schema errors before merge.
4. **Wire.** Update the relevant matrix row's `validation_commands` and `evidence_artifact` columns to reference the card and emitted evidence. Update the spine concept's `implemented_in` / `tested_by`.
5. **Pressure event.** Record a `SC-PRESSURE-*` event if the card materially changes how the concept is governed.

### Retrospective attestation

A card with `pre_registration.status = "retrospective"` is allowed, but the harness enforces a discipline:

- a retrospective PASS decision **must** include `retrospective`, `attestation`, or `not independent` in `decision.rationale`;
- the card is treated as an attestation of pre-existing evidence under the new schema, not as fresh evidence;
- two retrospective PASS cards do not equal one prospective PASS card; matrix rows that depend only on retrospective attestation should retain a follow-up `next_test` for prospective replication.

## 3) Required schema (leverage-card/v1)

A card is a JSON document with the following top-level keys (see `nfem_suite/intelligence/leverage/card.py` for the authoritative list):

| Field | Purpose |
|---|---|
| `card_id` | Stable identifier (`LEV-YYYY-MM-DD-NNN-slug`). |
| `schema_version` | Must equal `"leverage-card/v1"`. |
| `matrix_ref` | Matrix row this card feeds (e.g. `T-018`). |
| `concept_refs` | Spine concept IDs (e.g. `SC-CONCEPT-0010`). |
| `workflow` | `name`, `surface`, `domain`. |
| `claim_class` | List of `F` / `C` / `E` / `S`. |
| `claim_tier` | `defensible` / `plausible` / `speculative`. |
| `pre_registration` | `status`, `rationale`, `card_seal_commit`, `measurement_timestamp` (ISO 8601, prospective only). |
| `objective` | `statement`, `metric_name`, `metric_definition`, `threshold`, `direction`. |
| `baseline` | `name`, `source` (+ optional per-condition table). |
| `intervention` | `description`, `files` (+ optional `knobs`). |
| `denominators` | `compute`, `human_effort`, `evidence_cost` (and any optional axes). |
| `risk_vector` | `framework_gaming_risk`, `baseline_cherry_picking_risk`, `external_action_risk`, `irreversibility_risk` ∈ {`none`, `low`, `medium`, `high`}. |
| `reversibility` | `class` ∈ {`full`, `partial`, `none`}, `rollback_method`, `blast_radius`. |
| `verification` | `method` ∈ {`deterministic_recomputation`, `test_suite`, `stat_significance`, `human_audit`, `live_measurement`, `schema_validation`}, `validation_commands`, `evidence_artifacts`. |
| `failure_conditions` | Non-empty list of declared falsifiers. |
| `markers` | Subset of the FOUNDATIONS marker set. |
| `measured_outcome` | At minimum `summary`; structured `observations`, `fraction_satisfied`, `delta_vs_baseline_mean` recommended. |
| `decision` | `status` ∈ {`PASS`, `REVIEW`, `FAIL`}, `rationale`, optional `violated_markers`. |
| `provenance` | `authored_date`, `authored_by` (+ optional source concept, source pressure event). |

### Decision resolution

The scorer collapses the card to one decision:

- `decision.violated_markers` ∩ `{C1, I1, P1, P2}` → **FAIL** (hard gate).
- Seal verification fails (see below) → **FAIL**.
- Missing required fields, unknown markers, or other schema errors → **REVIEW**.
- Otherwise the declared `decision.status` stands.

This is the same hard-gate set used by `scripts/validate_foundations.py`, so a passing leverage card cannot pass while quietly violating a foundational marker.

### Seal-timestamp verification (prospective cards)

The harness will not accept a prospective card whose pre-registration seal happened *after* the measurement was taken. The check uses two fields and one git lookup:

- `pre_registration.card_seal_commit` — the commit hash that locks the card draft.
- `pre_registration.measurement_timestamp` — ISO 8601 timestamp recording when the measurement was actually taken.
- `git show -s --format=%cI <commit>` — the canonical committer timestamp of the seal commit.

Resolution table (only applies to `status == "prospective"`):

| Condition | `seal_verification` | Decision impact |
|---|---|---|
| seal commit timestamp ≤ measurement timestamp | `passed` | none (annotated in `notes`) |
| seal commit timestamp > measurement timestamp | `failed` | **FAIL** with `seal_after_measurement` error |
| `card_seal_commit` set, `measurement_timestamp` missing | `unverifiable` | warning only |
| git cannot resolve the commit | `unverifiable` | warning only |
| `git_lookup` not provided (e.g. in pure-schema unit tests) | `skipped` | none |
| No `card_seal_commit` set | (warning, not seal status) | warning only |

The CLI passes a real `git_show_committer_iso` lookup by default; unit tests inject a mock. The check is therefore enforced wherever the CLI runs (CI, local validation, matrix promotion) while remaining I/O-free in the pure scorer path.

The retrospective branch is unaffected: retrospective cards cannot be "sealed before measurement" by definition, so the scorer skips this check and relies on the existing attestation-disclosure rule instead.

## 4) Storage and naming

```
memory/research/leverage/
  YYYY-MM-DD-NNN-<slug>.json           ← the card
  YYYY-MM-DD-NNN-<slug>.evidence.json  ← scorer output (generated)
```

`card_id` should match the file stem. The evidence payload is a regeneratable artifact, but committing it makes diffs reviewable and lets the matrix link a stable path.

## 5) Wiring a card into the matrix

1. Add or update the matrix row's `Implementation surface` column to include the card path under `memory/research/leverage/`.
2. Set `Validation command(s)` to include
   `python3 scripts/run_leverage_card.py <card.json> --emit-evidence`.
3. Set `Evidence artifact` to the emitted `*.evidence.json` plus any underlying experimental artifacts referenced by `verification.evidence_artifacts`.
4. Update `Decision` to match the highest sustained card decision for this row. A row that has *only* retrospective attestation should remain at `REVIEW` *or* be marked `PASS (retrospective)` with an explicit `next_test` pointing at prospective replication.

## 6) Anti-gaming notes

The known failure modes of this protocol mirror the failure conditions on SC-CONCEPT-0010:

- *Denominator drift.* Once `pre_registration.card_seal_commit` is set, denominators and thresholds should not change. Edits after measurement are detectable in git history; reviewers should reject silent retunes.
- *Backdated seal.* Setting `card_seal_commit` to a commit hash that exists but post-dates the measurement is now a hard-FAIL via the seal-timestamp check above. Reviewers should still spot-check that the *content* sealed at that commit is actually the card draft, not unrelated work — the harness verifies timing, not semantic intent.
- *Self-referential closure.* The harness scores itself only via its first prospective card. That card explicitly notes its self-referential nature and the matrix row should remain `REVIEW` until at least one card scores PASS on an *independent* workflow.
- *Marker padding.* Listing many markers does not strengthen a card. The scorer accepts any subset of the FOUNDATIONS marker set; reviewers should reject cards whose markers do not correspond to claims actually exercised by the verification method.
- *Retrospective inflation.* Retrospective PASS cards are allowed but flagged; they do not on their own discharge a matrix row from `REVIEW`.

## 7) Pointers

- Harness: `nfem_suite/intelligence/leverage/`
- CLI: `scripts/run_leverage_card.py`
- Tests: `tests/test_leverage_card.py`
- Foundations validator interop: `scripts/validate_foundations.py`
- Concept: `docs/21_closed_loop_causal_leverage.md`, `spine/concepts/SC-CONCEPT-0010.yaml`
- Matrix row: `docs/theory-implementation-matrix.md` T-018
