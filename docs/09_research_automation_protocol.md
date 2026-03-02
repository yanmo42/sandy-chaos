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

## 4) Required artifacts per cycle

- `memory/research/<date>-query.md` — scoped question + constraints
- `memory/research/<date>-evidence.csv` — structured extraction table
- `memory/research/<date>-synthesis.md` — dual synthesis + confidence
- `memory/research/<date>-falsification.md` — explicit disproof conditions

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

## 9) Efficiency defaults

- Keep routine extraction/scripting on low thinking.
- Escalate thinking only for theory integration and contradiction resolution.
- Prefer short iterative cycles (30-90 min) over long monolithic runs.

## 10) Anti-hallucination guardrails

- Never treat uncited synthesis as evidence.
- Separate "what sources say" from "our interpretation".
- If evidence is weak or conflicting, output uncertainty explicitly.

This protocol is intentionally lightweight so it can run daily.
