# Concept Integrity Remediation Plan

**Repository:** `sandy-chaos`  
**Date:** 2026-02-27  
**Purpose:** Turn the documentation/theory stack into a tighter, falsifiable, internally consistent system; remove conceptual overreach; align docs with implemented reality.

---

## 1) Scope of this plan

This plan focuses on:

- Canonical docs (`docs/01`–`docs/06`, `glossary`, `math_appendix`, `math_foundations_zf`, docs README)
- Active planning docs (`plans/fix-list.md` + this plan)
- Implementation touchpoints where doc claims must cash out:
  - `nfem_suite/simulation/communication/temporal_protocol.py`
  - `nfem_suite/main.py`
  - `nfem_suite/simulation/temporal/tachyonic_loop.py`
  - `nfem_suite/formalization/complex_euler.py`
  - `nfem_suite/intelligence/entropy/shannon.py`
  - `nfem_suite/intelligence/cognition/idea_field.py`

Archive docs are treated as reference material, not canonical truth.

---

## 2) Executive diagnosis

The repo has strong ambition and some genuine rigor (claim tiers, falsification language, explicit causality boundaries), but currently suffers from **claim-tier drift** and **theory-implementation mismatch**.

### Main pattern

1. Defensible mechanisms are mixed with speculative metaphysics.
2. Some “resolved” theoretical language overstates what is actually derived/tested.
3. Protocol docs describe packet semantics that are not implemented in code.
4. Legacy terms (“tachyonic”) still appear in runtime/user-facing surfaces after conceptual correction.

Result: external readers can reasonably interpret stronger claims than the system can currently support.

---

## 3) Issue inventory (prioritized)

## CI-01 — Claim-tier leakage in Ouroboros + glossary
- **Severity:** Critical
- **Files:** `docs/06_observer_ouroboros.md`, `docs/glossary.md`
- **Symptoms:** Absolute/metaphysical language (“wrap reality perfectly”, substrate-level axiomatic embedding, predictive projection before explicit input).
- **Why this is a problem:** Conflicts with the project’s own causality + falsification discipline; reads as ontological claim, not testable model.
- **Fix direction:**
  - Rewrite `06` as a hypothesis/protocol note with explicit tier labels.
  - Move non-operational metaphysics into a clearly speculative subsection or archive.
  - Redefine glossary entries to operational, measurable terms only.

## CI-02 — Foundational overreach rhetoric in ZF document
- **Severity:** High
- **Files:** `docs/math_foundations_zf.md`
- **Symptoms:** Claims like “Nothing here is assumed. Everything is derived.” and “No step is arbitrary.”
- **Why this is a problem:** Conflates pure math derivability with empirical postulates/modeling choices (e.g., physical constants, metric choice, interpretation layer).
- **Fix direction:**
  - Add a **Formal Assumption Ledger** (math axioms vs physical postulates vs modeling conventions).
  - Replace absolutist language with bounded wording.
  - Keep derivation structure, but distinguish “logical consequence” from “framework choice”.

## CI-03 — Protocol documentation/code mismatch
- **Severity:** High
- **Files:** `docs/02_tempo_tracer_protocol.md`, `docs/math_appendix.md`, `docs/05_hyperstition_temporal_bridge_analysis.md`, `nfem_suite/simulation/communication/temporal_protocol.py`
- **Symptoms:** Docs describe richer packet schema (`validity_window`, trust metadata, narrative-boundary metadata) than implementation currently supports.
- **Why this is a problem:** Makes current capabilities look stronger than actual code.
- **Fix direction (choose one; recommended = A then B):**
  - **A (immediate):** Mark advanced packet fields as “planned extension” in docs.
  - **B (next):** Implement optional fields in `TemporalPacket` + decode-time checks + tests.

## CI-04 — Terminology debt: “tachyonic” still exposed
- **Severity:** High
- **Files:** `nfem_suite/main.py`, `nfem_suite/simulation/temporal/__init__.py`, comments/UI strings
- **Symptoms:** Console outputs and labels still use “Tachyonic Loop” despite docs clarifying entropic circulation/vortex charge.
- **Why this is a problem:** Reintroduces the exact overclaim that was supposed to be retired.
- **Fix direction:**
  - Keep backward-compatible class name if needed.
  - Rename all user-facing labels to **Entropic Circulation** / **Vortex Charge**.

## CI-05 — Open dynamics represented as conceptually mature
- **Severity:** Medium
- **Files:** `docs/05_hyperstition_temporal_bridge_analysis.md`, `docs/06_observer_ouroboros.md`, `plans/fix-list.md`
- **Symptoms:** Narrative-boundary dynamics and observer write-back are discussed at high confidence while key update laws (`\mathcal{G}`, domain-specific `\Phi`) remain unresolved.
- **Why this is a problem:** Readers cannot tell what is model vs placeholder.
- **Fix direction:**
  - Add explicit “Open Model Components” tables in relevant docs.
  - Require each unresolved component to list planned toy model + acceptance test.

## CI-06 — Entropy-causality bridge lacks literature anchoring
- **Severity:** Medium
- **Files:** `docs/05_hyperstition_temporal_bridge_analysis.md`, `plans/fix-list.md`
- **Symptoms:** Direction introduced but lightly connected to prior literature.
- **Why this is a problem:** Reinvention risk, credibility gap.
- **Fix direction:**
  - Add concise related-work section and delimitation statement.
  - Clearly state what is adopted vs what is novel.

## CI-07 — Public-facing synthesis doc overstates integration
- **Severity:** Medium
- **Files:** `docs/sandy_chaos_blog_synthesis.md`
- **Symptoms:** Highly polished integrated narrative can read as “already demonstrated”.
- **Why this is a problem:** Blurs roadmap vs validated results.
- **Fix direction:**
  - Add a short front-matter disclaimer with claim tiers and status.
  - Inline tag sections as Defensible / Plausible / Speculative.

---

## 4) “Bad ideas” to retire or quarantine

These are not banned forever, but must not be presented as active validated theory:

1. **Substrate-level “axiomatic injection” as if physically enforceable now**  
   Keep only as speculative governance metaphor unless implemented in explicit constraints.

2. **Predictive projection framing that implies pre-input mind certainty**  
   Reframe as probabilistic anticipatory prompting with uncertainty bounds.

3. **Absolute derivability rhetoric (“everything derived”, “no assumptions”)**  
   Replace with assumption-aware scientific framing.

4. **Any reappearance of “tachyonic” as user-facing semantics**  
   Keep alias only for compatibility; do not market/print as physical interpretation.

---

## 5) Remediation phases

## Phase 0 — Guardrails (Day 0–1)
**Goal:** Prevent further drift while edits proceed.

Tasks:
- Add a short “documentation status policy” section to `docs/README.md`:
  - every major claim must carry tier + failure condition,
  - speculative sections require explicit labeling.
- Add this plan as canonical remediation tracker in `plans/`.

Acceptance criteria:
- Policy text exists and is referenced from docs index.

## Phase 1 — Critical language cleanup (Day 1–2)
**Goal:** Remove most misleading conceptual claims.

Tasks:
- Rewrite `docs/06_observer_ouroboros.md` to:
  - keep usable observer-machine coupling concept,
  - remove absolute/metaphysical language,
  - add explicit claim tiers and failure conditions.
- Update `docs/glossary.md` entries:
  - tighten `Axiomatic Injection`, `Predictive Projection`, `Ouroboros Stabilization Effect` to operational wording.

Acceptance criteria:
- No canonical doc text implies perfect prediction/control.
- Glossary terms are measurable or clearly tagged speculative.

## Phase 2 — Docs-to-code protocol alignment (Day 2–3)
**Goal:** Make communication claims truthful to implementation.

Tasks:
- Decide scope:
  - **Minimal:** downscope docs to current `TemporalPacket` fields.
  - **Preferred:** implement optional packet fields (`validity_window`, `narrative_context`, `boundary_tag`, `audit_trace`) in `temporal_protocol.py`.
- If implemented, add tests for:
  - checksum validation,
  - validity window logic,
  - optional metadata passthrough.

Acceptance criteria:
- Packet schema in docs equals schema in code (or explicitly marked roadmap).

## Phase 3 — Terminology and surface consistency (Day 3)
**Goal:** Remove residual overclaim terms from runtime outputs.

Tasks:
- In `nfem_suite/main.py`, rename user-facing strings:
  - “Tachyonic Loop Detection” → “Entropic Circulation Detection”
  - “TEMPORAL LOOP DETECTED” → “ENTROPIC CIRCULATION DETECTED”
  - “Tachyonic Loops” summary → “Entropic Circulation Loops”
- Optionally add alias class `EntropicCirculation` wrapping `TachyonicLoop` for migration.

Acceptance criteria:
- No user-facing runtime output uses tachyonic terminology.

## Phase 4 — Theoretical hygiene pass (Day 4–5)
**Goal:** Keep high ambition without overclaiming.

Tasks:
- Revise `docs/math_foundations_zf.md` preamble + conclusion:
  - add assumption ledger,
  - soften necessity claims,
  - preserve useful formal chain.
- In `docs/05_hyperstition_temporal_bridge_analysis.md`:
  - separate established model from speculative bridge language,
  - add related-work pointers and novelty delimitation.

Acceptance criteria:
- Readers can clearly separate formal derivation, empirical assumption, and speculative interpretation.

## Phase 5 — Open-model closure plan (Week 2)
**Goal:** Convert placeholders into testable mini-models.

Tasks:
- Add toy model spec for narrative dynamics `\mathcal{G}` (2-agent, 2-narrative system).
- Add concrete fluid-domain instantiation for observer write-back `\Phi`.
- Add acceptance tests and expected failure modes.

Acceptance criteria:
- Each previously “open” component has a testable minimal model.

---

## 6) File-level edit map

## Immediate edits (high confidence)
- `docs/06_observer_ouroboros.md` — major rewrite (critical)
- `docs/glossary.md` — term tightening (critical)
- `docs/README.md` — policy addition
- `docs/sandy_chaos_blog_synthesis.md` — claim-tier front-matter disclaimer
- `nfem_suite/main.py` — terminology cleanup

## Next edits (after decision on schema scope)
- `docs/02_tempo_tracer_protocol.md`
- `docs/math_appendix.md`
- `docs/05_hyperstition_temporal_bridge_analysis.md`
- `nfem_suite/simulation/communication/temporal_protocol.py`
- tests for protocol packet behavior

## Foundation cleanup
- `docs/math_foundations_zf.md` — assumption-aware framing revision

---

## 7) Governance gates (must pass before merge)

1. **Tier Gate:** Every major claim in canonical docs has tier label.
2. **Falsification Gate:** Defensible/plausible claims include failure conditions.
3. **Implementation Truth Gate:** Docs do not claim fields/features absent from code unless explicitly marked planned.
4. **Terminology Gate:** No backward-causation-implying language in user-facing text.
5. **Speculation Boundary Gate:** Ontological/philosophical content is isolated and labeled.

---

## 8) Quick verification checklist

- [x] `docs/06` rewritten with explicit tiering and no absolute certainty language
- [x] `glossary` terms aligned with measurable semantics
- [x] packet schema parity achieved (or roadmap-marked)
- [x] no runtime “tachyonic” UI strings remain
- [x] `math_foundations_zf` includes assumption ledger and toned claims
- [x] synthesis/blog doc carries status disclaimer

---

## 9) Definition of done

This remediation is complete when:

1. A skeptical reader can identify exactly which claims are currently defensible.
2. No canonical doc implies stronger physics/agency conclusions than code and tests support.
3. Speculative ideas remain present but clearly sandboxed.
4. Terminology no longer undermines the project’s stated causality discipline.

At that point, the repo can continue ambitious theory-building without sacrificing conceptual integrity.