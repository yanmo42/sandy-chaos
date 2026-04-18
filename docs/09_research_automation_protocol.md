# 09 Research Automation Protocol (Efficient + Reproducible)

## 1) Objective

Define a practical AI workflow for research automation that maximizes speed **without sacrificing** reproducibility, source traceability, and falsification discipline.

## 2) Core principle

Use AI agents for parallelization and synthesis; keep humans in control of:
- scope boundaries,
- inclusion/exclusion criteria,
- final claims.

## 3) Operating loop

1. **Frame question** with bounded claim tier + failure condition.
2. **Collect evidence in parallel** (search/fetch across multiple sources).
3. **Extract into schema** (method, assumptions, metrics, limitations, citation).
4. **Dual synthesis**:
   - supportive synthesis (best-case interpretation),
   - adversarial synthesis (failure modes / counter-evidence).
5. **Verifier pass**:
   - citation validity,
   - contradiction scan,
   - claim-tier compliance.
6. **Artifact commit** (notes, evidence table, summary, next action).

Across continuity cadences, this loop should be read as an explicit surface map rather than an implicit tempo metaphor:

- collection and extraction work usually belongs to the **edge / fast** layer,
- verifier synthesis, cycle summaries, and continuity-contract routing belong to the **bridge / meso** layer,
- promoted docs, workflow rules, and test-bearing expectations belong to the **spine / slow** layer.

That mapping is strictly forward-causal. Fast research artifacts can inform bridge summaries, and bridge summaries can justify slow-surface promotion, but the protocol should not imply raw fast-loop output directly rewriting spine surfaces.

## 4) Required artifacts per cycle

- `memory/research/<date>-query.md` — scoped question + constraints
- `memory/research/<date>-evidence.csv` — structured extraction table
- `memory/research/<date>-synthesis.md` — dual synthesis + confidence
- `memory/research/<date>-falsification.md` — explicit disproof conditions

Every cycle should also end with an explicit continuity contract in the research task artifact:

- `branch_outcome_class` (`local` | `promotable` | `policy-relevant` | `blocked`)
- `disposition` (`DROP_LOCAL` | `LOG_ONLY` | `TODO_PROMOTE` | `DOC_PROMOTE` | `POLICY_PROMOTE` | `ESCALATE`)
- `promotion_target` (`todo` | `docs` | `workflow` | `foundations` | `tests/config` | `log-only`)
- `next_action` (single concrete line)

(Directory path can be adjusted; structure is the important part.)

## 5) Minimal schema (evidence rows)

Each source row should include:
- source_id
- url / DOI
- claim_supported
- method_type
- dataset/context
- key_result
- limitation
- extraction_confidence (low/med/high)
- reviewer_status (pending/accepted/rejected)

## 6) Claim-tier policy (must be explicit)

- **Defensible:** directly supported by cited evidence + reproducible extraction trail
- **Plausible:** partially supported, unresolved counterpoints listed
- **Speculative:** hypothesis/roadmap only, clearly labeled as non-validated

No mixed-tier paragraphs without labels.

## 7) Quality gates

A cycle is complete only if all gates pass:

1. At least 2 independent sources for each non-trivial claim.
2. Every summary claim maps to one or more source rows.
3. At least one counterargument is documented for central claims.
4. Final output includes a concrete next experiment/check.
5. Synthesis includes a `## Claims` section where each bullet has source tags like `[S001]`.

Verifier command:

```bash
python3 scripts/research_verifier.py --synthesis memory/research/<date>-synthesis.md --evidence memory/research/<date>-evidence.csv
```

## 8) OpenClaw lane mapping

- **planner lane:** scope, criteria, and task contracts
- **builder lane:** extraction scripts and evidence artifacts
- **verifier lane:** contradiction/citation checks
- **reporter lane:** concise decision memo + next best action

The lane split should also respect cadence placement:

- planner/builder work often starts at the **edge / fast** layer,
- verifier/reporter outputs usually form the **bridge / meso** layer,
- only reviewed promotions from those outputs should update **spine / slow** surfaces such as canonical docs, workflow policy, or tests/config.

## 9) Efficiency defaults

- Keep routine extraction/scripting on low thinking.
- Escalate thinking only for theory integration and contradiction resolution.
- Prefer short iterative cycles (30-90 min) over long monolithic runs.

## 10) Anti-hallucination guardrails

- Never treat uncited synthesis as evidence.
- Separate "what sources say" from "our interpretation".
- If evidence is weak or conflicting, output uncertainty explicitly.

This protocol is intentionally lightweight so it can run daily.

## 11) Daily automation hook (active-cycle summary)

`self_improve.py full-pass` now includes a research-cycle summary hook:

- It scans `memory/research/` for today's cycle bundles (`*-query/evidence/synthesis/falsification`).
- It treats a cycle as active when at least one artifact in a complete bundle was updated in the last 24 hours.
- When active, it writes or refreshes exactly one summary artifact per cycle prefix:
  - `memory/research/<date-or-date-slug>-cycle-summary.md`
- The summary is descriptive only (strictly forward-causal) and includes evidence row count, unique source count, and synthesis claim-bullet count.
- Full-pass and cadence digests should also surface the latest continuity contract distributions (branch outcome classes, dispositions, promotion targets) from orchestrator artifacts.

## 12) Anchor + retrodiction mini-protocol (v0, strict + compact)

Use this extension when a cycle claims present-world anchoring, bounded-now quality, or retrodictive reconstruction.

### 12.1 Required anchor ladder row (per active channel)

Each cycle should add one row per anchor channel in `memory/research/<date>-anchors.csv` with:

- `anchor_id`
- `channel_type` (`internet-log` | `telemetry` | `camera-audio` | `multimodal` | `other`)
- `latency_ms_p50`
- `latency_ms_p95`
- `fidelity_score` (0-1)
- `provenance_level` (`weak` | `medium` | `strong`)
- `adversarial_risk` (`low` | `med` | `high`)
- `trace_persistence` (`ephemeral` | `short` | `durable`)

### 12.2 `Q_now` provisional metric fields

For each cycle that uses anchors, report:

- `q_now_score` (0-1)
- `q_now_latency_component` (0-1)
- `q_now_provenance_component` (0-1)
- `q_now_noise_component` (0-1)
- `q_now_calibration_component` (0-1)
- `q_now_coverage_component` (0-1)

Write these into `memory/research/<date>-qnow.json`.

### 12.3 Backaction regime tags

Every anchor/reconstruction cycle must declare one tag:

- `passive` (backaction negligible)
- `weak-coupled`
- `strong-coupled`
- `control-dominant` (measurement policy likely shapes trajectory)

Store tag + rationale in `memory/research/<date>-query.md`.

### 12.4 Retrodictive benchmark task template

Each retrodictive task should include:

- `task_id`
- `domain`
- `target_event_window`
- `available_trace_set`
- `null_model`
- `reconstruction_method`
- `success_metrics` (at least one calibration metric + one accuracy metric)
- `abstention_rule`
- `failure_condition`

Store tasks in `memory/research/<date>-retrodiction_tasks.json`.

### 12.5 Abstention + uncertainty gates (hard requirements)

For any retrodictive claim beyond descriptive logging:

1. report uncertainty (confidence interval or calibrated uncertainty band),
2. apply the declared abstention rule,
3. mark outputs as `ABSTAIN` when evidence quality is below threshold,
4. do not promote `ABSTAIN` results into policy-bearing surfaces.

If any gate is missing, cycle status is `REVIEW` (not `PASS`).
