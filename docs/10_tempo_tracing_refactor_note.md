# 10 Tempo Tracing Refactor Note

## Intent

This note records a planned naming and framing refactor:

- **from:** Tempo Tracer
- **to:** Tempo Tracing

Working thesis statement:

> **Tempo tracing — a novel method of leveraging temporal differences in computing to exploit almost paradoxical informational advantages.**

The refactor is semantic, architectural, and communication-facing: move from a tool/object framing ("tracer") to a method/process framing ("tracing").

---

## Why this change

- "Tracer" implies a fixed component.
- "Tracing" better matches the project’s current direction: continuous, testable inference over cross-frame temporal structure.
- The method framing aligns with existing causality guardrails (forward dynamics only) and claim-tier discipline.

---

## Claim tiers (for this refactor)

### Defensible now

- Renaming to **Tempo Tracing** improves conceptual alignment with process-level protocol language already used in docs and simulation metrics.
- The framework remains causality-safe: no ontic backward causation claims are introduced by this terminology shift.

### Plausible but unproven

- A method-centric framing may improve onboarding clarity and reduce misreadings as a single black-box algorithm.

### Speculative

- The "almost paradoxical informational advantages" framing could catalyze better research ideation without increasing conceptual drift.

---

## Non-negotiable boundaries

- No retrocausal physical claims.
- No superluminal operational claims.
- All "future-like" effects must reduce to forward-time dynamics, temporal asymmetry, and inference.

---

## Failure conditions

This refactor should be considered unsuccessful if any of the following occur:

1. **Causal ambiguity increases:** contributors interpret Tempo Tracing as permitting backward physical influence.
2. **Validation quality drops:** docs stop requiring explicit falsification criteria for major claims.
3. **Implementation drift:** naming changes are not reflected in protocol-language touchpoints, producing inconsistent terminology across docs/code/tests.
4. **Signal loss:** the new framing obscures practical metrics (directional capacity, asymmetry, calibration, reproducibility).

---

## Integration scope

Near-term documentation integration should focus on:

- protocol language in `02_tempo_tracer_protocol.md`,
- glossary harmonization,
- roadmap/automation references where "tracer" implies a static module instead of a method.

This note proposes **incremental migration** (compatibility wording: "Tempo Tracing (formerly Tempo Tracer)") rather than disruptive renaming in one pass.
