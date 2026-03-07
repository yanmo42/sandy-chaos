# Research Ingestion Protocol (Literature → Claims → Experiments)

## 1) Objective

Create a reproducible ingestion pipeline that converts external scientific literature
(textbooks, papers, reviews, preprints) into:

1. structured, auditable claim units,
2. Sandy Chaos ontology mappings,
3. falsifiable experiment candidates.

This protocol extends `09_research_automation_protocol.md` and specializes the **front-end ingestion layer**.

---

## 2) Design principles

- **Rigor first:** preserve source traceability down to paragraph/equation level.
- **Dual expression:** each accepted concept must have both:
  - a formal/symbolic expression,
  - a plain-language explanation.
- **Claim-tier discipline:** defensible / plausible / speculative must be explicit.
- **Falsification-first:** every major claim includes a failure condition.
- **No silent synthesis:** interpretation is separated from source-grounded extraction.

---

## 3) Scope and source classes

In-scope source types:

- peer-reviewed papers,
- major textbooks/monographs,
- high-quality review articles,
- methods papers and benchmark datasets.

Out-of-scope (unless explicitly approved for ideation-only lanes):

- unsourced blog claims,
- social-media summaries,
- citation-free generated text.

---

## 4) Canonical data products per ingestion cycle

For cycle prefix `<cycle-id>` (e.g., `2026-03-07-tempo-entropy`), generate:

- `memory/research/<cycle-id>-query.md`
- `memory/research/<cycle-id>-sources.csv`
- `memory/research/<cycle-id>-claims.csv`
- `memory/research/<cycle-id>-mapping.md`
- `memory/research/<cycle-id>-hypotheses.md`
- `memory/research/<cycle-id>-falsification.md`
- `memory/research/<cycle-id>-cycle-summary.md`

---

## 5) Pipeline stages

### Stage A — Question framing

Define:

- target question,
- claim-tier target,
- inclusion/exclusion criteria,
- mandatory failure tests for central hypotheses.

Output: `<cycle-id>-query.md`

### Stage B — Source harvesting

Harvest and normalize metadata:

- DOI/URL,
- title,
- authors,
- venue,
- year,
- method category,
- domain tags.

Output: `<cycle-id>-sources.csv`

### Stage C — Atomic extraction

Extract source-grounded atomic units:

- claim text (verbatim or close paraphrase),
- evidence type (theory / simulation / experiment / review),
- assumptions,
- equations/metrics,
- stated limitations.

Output: `<cycle-id>-claims.csv`

### Stage D — Ontology mapping (Sandy Chaos)

Map each extracted claim to one or more ontology anchors:

- entropy dynamics,
- temporal asymmetry,
- observer read-write coupling,
- control policy / agency,
- causal guardrails,
- falsification metric.

Output: `<cycle-id>-mapping.md`

### Stage E — Hypothesis synthesis (dual block format)

For each candidate concept, produce:

1. **Formal block** (symbols, constraints, measurable predictions)
2. **Language block** (intuition, mechanism narrative, boundary conditions)

and assign claim tier + confidence.

Output: `<cycle-id>-hypotheses.md`

### Stage F — Falsification and experiment queue

Convert top candidate hypotheses into test cards with:

- expected signal,
- competing null,
- minimum evidence threshold,
- explicit stop/fail condition,
- required implementation/test harness.

Output: `<cycle-id>-falsification.md`

---

## 6) Minimum schemas

### 6.1 `sources.csv`

Required columns:

- `source_id`
- `type` (paper|textbook|review|preprint)
- `title`
- `authors`
- `year`
- `venue`
- `doi_or_url`
- `domain_tags`
- `quality_score` (low|med|high)

### 6.2 `claims.csv`

Required columns:

- `claim_id`
- `source_id`
- `claim_text`
- `claim_kind` (empirical|theoretical|methodological)
- `equation_or_metric`
- `assumptions`
- `limitations`
- `supports_topic`
- `claim_tier` (defensible|plausible|speculative)
- `extraction_confidence` (low|med|high)

---

## 7) Quality gates (must pass)

1. **Traceability gate:** each synthesized claim links to at least one `claim_id`.
2. **Coverage gate:** each non-trivial hypothesis has at least two independent sources.
3. **Contradiction gate:** central contradictions are listed (not hidden).
4. **Tier gate:** mixed-tier statements are split into separate bullets.
5. **Falsification gate:** every major hypothesis has measurable fail criteria.
6. **Separation gate:** source statements and interpretation are explicitly separated.

If any gate fails, cycle status is `incomplete`.

---

## 8) Failure conditions for this protocol

The ingestion protocol is failing if:

- outputs become citation-thin (claims cannot be traced to specific source units),
- speculative language is presented as defensible result,
- experiment queue items lack null models or stop criteria,
- ontology mappings are inconsistent across cycles,
- cycle artifacts are not reproducible from recorded inputs.

---

## 9) Integration with `ferroelectric-materials-project`

Use Ian’s public research library as the ingestion engine for Stages B/C:

- source collection and metadata normalization,
- text extraction and chunking,
- candidate claim/equation extraction.

Sandy Chaos-specific additions happen in Stages D/E/F:

- ontology mapping,
- claim-tier assignment,
- falsification queue generation.

Implementation guidance:

- keep external ingestor and Sandy Chaos mapper as separate modules,
- preserve stable IDs (`source_id`, `claim_id`) across reruns,
- write deterministic CSV/Markdown artifacts for diff-friendly review.

---

## 10) Operational cadence

Default cadence:

- 1 light ingestion cycle/day (30–60 min),
- 1 deeper synthesis cycle/week (2–4 h),
- monthly consolidation into long-term docs.

---

## 11) Immediate next action

Run a pilot on one narrow theme:

**"Temporal asymmetry metrics under observer-coupled channels"**

and produce one complete `<cycle-id>` bundle to validate the protocol end-to-end.
