# Lux–Nyx Interaction Contract v0

**Status:** bounded interaction draft  
**Date:** 2026-03-30  
**Claim tier:** operational/plausible framing with explicit future implementation targets  
**Intended role:** describe a typed interaction grammar that can later be implemented in code and evaluated against concrete routing / suggestion / governance outcomes

## Purpose

Convert the Lux / Nyx / shadow operator grammar into an interaction contract that can be implemented, inspected, and pressure-tested.

This note does **not** claim that Lux/Nyx is already a canonical Sandy Chaos subsystem.
It claims something narrower:

> Sandy Chaos may benefit from a typed interaction layer in which arriving inputs are classified, bent through bounded transforms, and emitted as trace-bearing artifacts instead of unshaped suggestions or suppressed intuition.

The goal is to formalize the earlier symbolic grammar:

- **Lux** = arrival / surfacing / activation pressure
- **Nyx** = curvature / gating / weighting / compression pressure
- **Shadow** = the trace-bearing artifact produced when visibility acquires cost

Compressed version:

> **Lux moves. Nyx bends. Shadow remembers.**

## Why this belongs in the codebase

Sandy Chaos already has:
- predictive-loop language,
- governance / promotion gates,
- continuity / trace concerns,
- subsystem and membrane records,
- and an increasing need for bounded interaction contracts.

What is still missing is a shared grammar for:
- what kind of input just arrived,
- how strongly it should be surfaced,
- which transforms are allowed,
- what artifact must remain afterward,
- and how to tell whether that shaping helped.

Without this layer, the project risks two opposite failures:
- **glare** — too much raw surfacing without constraint,
- **collapse** — too much compression or withholding without usable output.

## Core contract shape

Each interaction instance should eventually declare at least:

- `input_type`
- `input_description`
- `salience`
- `ambiguity`
- `risk`
- `evidence_tier`
- `urgency`
- `privacy_level`
- `allowed_nyx_ops`
- `shadow_artifact_type`
- `shadow_artifact_summary`
- `promotion_condition`
- `failure_condition`
- `trace_requirements`

This is the minimum useful shape for turning the metaphor into a runtime-usable contract.

## Lux input classes

Initial input classes:

1. **spark**
   - new idea fragment
   - often high salience, high ambiguity
2. **prompt**
   - direct next-action request
   - typically needs ranking and compression more than archival handling
3. **push**
   - strong impulse toward action, publication, or escalation
   - requires risk-aware gating
4. **claim**
   - statement that may need tiering and falsification framing
5. **signal**
   - external event, anomaly, alert, or notification
6. **route-request**
   - "where should this go?"
7. **symbolic-input**
   - naming, persona, mythic, or operator-heavy material

These classes are intentionally practical, not exhaustive.

## Nyx transform set

Initial allowed Nyx operations:

- **gate** — allow / hold / reject
- **compress** — shorten while preserving contour
- **weight** — assign seriousness / consequence density
- **tier** — mark defensible / plausible / speculative
- **delay** — hold for later review under explicit revisit conditions
- **mask** — partial reveal only
- **trace** — preserve provenance and transformation path
- **split** — one input becomes multiple downstream outputs with distinct handling

A future implementation should treat these as operators with explicit preconditions and failure modes, not as vibes.

## Shadow artifact taxonomy

Initial artifact types:

- **glint** — brief preview or early hint
- **contour** — summary preserving shape without full exposure
- **draft** — bounded, revisable output
- **queue-item** — deferred artifact with revisit trigger
- **promotion-candidate** — survived enough pressure to move upward
- **audit-trace** — why a gate, delay, or transformation happened
- **refusal-artifact** — a no-with-reason rather than silent disappearance

Rule:

> No Nyx transform should occur without a declared shadow artifact or an explicit refusal artifact.

Otherwise the system becomes opaque and self-sealing.

## Interaction regions

Useful first interaction regions:

### 1. High salience, low ambiguity, low risk
Examples:
- routine next-step suggestions
- obvious route hints
- lightweight interface nudges

Expected Nyx pattern:
- minimal compression
- ranking
- trace-light handling

Expected shadow output:
- `glint`
- or concise `contour`

### 2. High salience, high risk
Examples:
- canonical promotion
- public publication
- consequential repo changes
- governance-affecting claims

Expected Nyx pattern:
- hard gating
- evidence-tier check
- explicit promotion condition
- audit trace required

Expected shadow output:
- `draft`
- `promotion-candidate`
- or `refusal-artifact`

### 3. High ambiguity, symbolic or interpretive input
Examples:
- naming material
- symbolic maps
- architectural intuitions without evidence maturity

Expected Nyx pattern:
- preserve without over-promoting
- compress and trace
- route into archive, map, or question bundle

Expected shadow output:
- `contour`
- `draft`
- or `queue-item`

### 4. Low salience, high evidence
Examples:
- boring but solid operational facts
- stable checks
- routine maintenance truths

Expected Nyx pattern:
- low-drama structuring
- direct trace

Expected shadow output:
- `audit-trace`
- `draft`
- or direct structured record

## Candidate pilot surfaces

This framework should not be declared canonical until it proves useful on at least one narrow surface.

Best pilot surfaces:

1. **next-action suggestion shaping**
   - likely highest value
   - cleanest metrics
2. **doc promotion / archive routing**
   - already closely aligned with existing Sandy Chaos habits
3. **interaction trace capture**
   - useful if the system starts preserving why an answer was shaped a certain way

Recommendation:

> Pilot on **next-action suggestion shaping** first, then extend to doc promotion if results are positive.

## Measurable success criteria

A Lux–Nyx interaction layer is only useful if it improves outcomes.

Candidate observables:
- suggestion acceptance rate
- edit distance from surfaced suggestion to accepted action
- correction burden
- latency-to-useful-action
- overexposure rate
- false-withholding rate
- archive-to-promotion conversion quality
- trace completeness for gated decisions

## Claim tiers

### Defensible now
- Sandy Chaos would benefit from a typed interaction contract for shaping arriving inputs into bounded outputs.
- The Lux / Nyx / shadow grammar offers a compact and memorable way to describe surfacing, constraint, and trace.
- The proposed record fields are implementable as a lightweight artifact surface.

### Plausible but unproven
- A Lux–Nyx contract could improve next-action suggestion quality and reduce both overexposure and overcompression failure modes.
- The grammar may become useful across interaction, governance, and continuity surfaces.

### Speculative
- That Lux / Nyx becomes a broadly load-bearing architectural layer rather than a strong local interaction grammar.
- That the framework scales cleanly beyond suggestion / routing / archive use cases.

## Pilot Measurement Implementation

As of April 2026, the pilot on **next-action suggestion shaping** includes a tracking layer to validate the contract against pre-Lux-Nyx baselines.

### Tracked Metrics
- **Suggestion Acceptance Rate**: Ratio of suggestions accepted without manual correction.
- **Correction Burden**: Quantitative measure of manual edits required after a suggestion is surfaced.
- **Archive-to-Promotion Conversion Quality**: Qualitative and quantitative tracking of whether items routed to archive eventually surface as high-quality promotion candidates.

### Baseline Comparison
Metrics are tracked in `state/lux_nyx/metrics.json` and compared against pre-Lux-Nyx baseline estimates to prove operational value before further architectural promotion.

The baseline is now an explicit frozen surface rather than an implicit all-zero default: use `python3 scripts/lux_nyx_pilot_baseline.py --suggestion-acceptance-rate <x> --correction-burden-per-suggestion <y> --archive-to-promotion-conversion-quality <z>` to write the pre-Lux-Nyx comparison reference without resetting live counters.

Live pilot events can now be logged one causal step at a time with `python3 scripts/lux_nyx_pilot_event.py`: `--suggestion <action>` records a shaped suggestion, `--accept` / `--reject` records whether that surfaced suggestion was taken as-is, `--corrections <n>` records manual correction burden, and `--archive-to-promotion` records the later archive → promotion conversion when that cross-session transition actually happens. Governance routing alone does **not** auto-record acceptance or rejection anymore; a suggestion only counts as accepted once a later explicit causal event says it was actually taken without correction.

`--suggestion` now accepts only the canonical evaluator action names (`keep`, `compress`, `archive`, `route`, `hold`, `promote-candidate`, `refuse-with-reason`) so pilot counters cannot silently drift from the actual Lux–Nyx action grammar because of typos or ad-hoc labels.

The event recorder now enforces that ordering explicitly: acceptance and correction events require at least one previously recorded suggestion, and archive → promotion events require a previously recorded archive suggestion. This keeps the pilot counters causally honest instead of allowing retroactive conversion or acceptance counts to outrun their antecedent suggestions.

One narrow workflow auto-wire now exists for that last metric: when `scripts/self_improve.py promote-policy-tweaks` promotes a tweak carrying explicit archive-origin metadata (`pilot_archive_origin: true`, `lux_nyx_shaping.archive_origin: true`, or `lux_nyx_shaping.prior_destination: "archive"`), it records the archive → promotion conversion automatically instead of requiring a separate manual CLI step.

Until that freeze step happens, `state/lux_nyx/pilot_report.json` marks baseline comparison entries as `direction: "unconfigured"` with `baseline` / `delta` left null, so the pilot does not claim false lift against a synthetic zero baseline.

## Failure conditions

This effort fails if:
- the grammar stays purely aesthetic,
- Nyx becomes a synonym for obscurity instead of bounded transform,
- shadow artifacts are too vague to audit,
- the system gets slower without improving decision quality,
- or the interaction layer cannot be connected to measurable outcomes.

## Promotion condition

Promote this beyond bounded draft status only if:
- a pilot implementation exists,
- metrics show reduced mismatch or improved routing quality,
- transformation traces are inspectable,
- and the contract clearly improves at least one real workflow.

## Immediate next action

Use this document as the conceptual contract for:
- a typed artifact template,
- a subsystem record,
- a membrane record,
- and a minimal code scaffold for loading and validating Lux–Nyx interaction records.
