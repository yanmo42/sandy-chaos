# Self-Referential Tempo Edge (ADR-23)

**Status:** proposed
**Date:** 2026-06-06
**Concepts:** SC-CONCEPT-0003 (hyperstition / observer coupling), SC-CONCEPT-0010 (closed-loop causal leverage)
**Companion docs:** [24 — Tempo Edge Redaction Policy](24_tempo_edge_redaction_policy.md)
**Companion schema:** [`schemas/tempo_point_v0.schema.json`](../schemas/tempo_point_v0.schema.json)

## Context

The Sandy Chaos research engine has, until now, run almost entirely on synthetic toy models (hyperstition Arm A grids, leverage card simulations). The framework's central claims — observer coupling, closed-loop causal leverage, bidirectional corridors — assume an embedded operator emitting decisions under bounded resources. The toy models substitute mathematical operators for that embedded entity.

The next defensible step is to begin sampling a real embedded operator: the human running the system. Gameplay + input streams (SC2 first, input-only fallback for other titles) are a clean source because:

- the operator is the same person who built the framework, so the loop is genuinely self-referential rather than third-party-observed;
- the decision rate is high enough to produce statistically interesting tempo points within a single session;
- game-state coupling (where available) lets us pair input with outcomes inside a bounded environment;
- the surface is already part of the operator's life (Hxvn content workflow), so the data-collection burden is incremental.

## Decision

Build a **telemetry edge** that ingests gameplay + input streams and emits structured **tempo points** to the research engine.

- **Edge:** JavaScript/TypeScript (Node), running in-process on the operator's machine. Lives in `telemetry-edge/` inside the sandy-chaos repo (single repo, clear seam, extractable later if it grows up).
- **Core:** existing Python research engine (`nfem_suite/`, `scripts/`, leverage harness).
- **Wire format:** `tempo_point_v0.schema.json`. Edge emits JSON Lines; core consumes them.

The edge is responsible for everything that touches raw input: capture, ring-buffer, aggregation, redaction, emission. The core is responsible for analysis: scoring, corridor detection, leverage attribution.

This separation is normative: **no raw keystrokes, raw chat text, or untrimmed input streams ever cross the seam**. The redaction policy ([doc 24](24_tempo_edge_redaction_policy.md)) is part of the seam contract, not an afterthought.

## Architecture

```
+------------------------+      +-----------------------+      +------------------------+
| capture layer          |      | edge aggregator       |      | research core (Python) |
| - game-state listener  |  ->  | - in-memory ring buf  |  ->  | - tempo point ingest   |
| - input listener       |      | - windowed aggregates |      | - SC corridor scoring  |
| - clock                |      | - redaction filter    |      | - leverage attribution |
+------------------------+      +-----------------------+      +------------------------+
        |                                |                                |
   raw events                  tempo_point_v0 JSONL              memory/research/
   (never persisted)           (only persisted form)              tempo/<session>/
```

### Coupling/decoupling framing (operator-supplied, plausible tier)

Operator vision: tempo points should be readable as **coupling and decoupling events** between the operator's intent surface and the game's state surface. Tight coupling = APM windows where input rate, game-state change rate, and decision-flag density rise together. Decoupling = windows where one of those terms moves without the others. This framing is treated as a *plausible* analytic lens, not a load-bearing assumption: the schema records the raw aggregates, and coupling/decoupling is computed downstream so the lens can be revised without invalidating collected data.

## Wire format (summary)

Full schema: [`schemas/tempo_point_v0.schema.json`](../schemas/tempo_point_v0.schema.json).

A tempo point is a window summary, not an event. Required fields:

- `ts` — ISO-8601 timestamp of window end
- `session_id` — opaque per-session identifier (no operator PII)
- `source` — taxonomy: `game:sc2`, `game:arc-raiders`, `game:fortnite`, `input:keyboard`, `input:mouse`, `mixed`
- `window_ms` — window length the aggregates cover
- `point_kind` — one of: `apm_window`, `interval_cluster`, `decision_flag`, `game_state_delta`
- `aggregates` — typed bag of numeric/categorical aggregates appropriate to the `point_kind`
- `redaction_version` — version of the redaction policy active at emit time

Forbidden fields (schema enforces `additionalProperties: false` and explicit `not` constraints):

- any `raw_*` field, any `*_keys` field containing key sequences, any `text` field with free-form characters

## Claim tiers

- **Defensible now:** the edge can capture operator tempo at session granularity with redaction-by-construction; the wire format separates capture from analysis; the seam is auditable.
- **Plausible but unproven:** tempo points sampled from real operator sessions will show distributional structure analogous to the corridors observed in the hyperstition toy model. (Falsifiable: if a session-corpus pressure event scores no corridor coverage above chance, the bridge is weakened.)
- **Speculative:** the coupling/decoupling framing generalizes beyond gameplay to any operator-environment pair. (Out of scope for this ADR; recorded so claim drift can be policed.)

## Failure conditions

- Raw keystrokes, raw chat text, or any verbatim input characters land on persistent storage. → safety fail, edge must be halted and audited.
- The wire schema is edited *after* a measurement window opens, in a direction that changes what counts as a valid tempo point. → seal violation by analogy with the leverage card protocol (doc 22).
- "Coupling" becomes synonymous with "any correlation between input and game state." → claim drift; concept needs a sharper operational definition before further commits.
- A tempo point includes fields not declared in `tempo_point_v0`. → contract violation; edge must be patched or schema versioned forward.

## What this ADR does NOT decide

- Specific game-state parser implementations (SC2 replay parser library, etc.) — chosen during Medium scope.
- Whether the edge eventually publishes anything to npm. Default: **no**, the edge is a local tool. Any publication is a separate calm-confirmation decision.
- Long-term storage layout beyond the `memory/research/tempo/<session>/` convention.
- Cross-operator data (only the single embedded operator is in scope).

## Next steps

1. **Small (this commit):** ADR + redaction policy + schema, no executable code.
2. **Medium (next, gated on operator review of this ADR):** one Node module that reads a sample SC2 replay + a sampled input stream and emits valid `tempo_point_v0` JSONL.
3. **Large (later, separately gated):** live session capture, multi-session corpus, first prospective leverage card on a tempo-edge workflow.
