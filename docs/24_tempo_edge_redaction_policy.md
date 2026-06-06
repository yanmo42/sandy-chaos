# Tempo Edge Redaction Policy (v0)

**Status:** normative, version `v0`
**Date:** 2026-06-06
**Applies to:** any code in `telemetry-edge/` or any other surface that ingests operator input or game state for the Sandy Chaos research engine.
**Companion ADR:** [23 — Self-Referential Tempo Edge](23_self_referential_tempo_edge.md)
**Companion schema:** [`schemas/tempo_point_v0.schema.json`](../schemas/tempo_point_v0.schema.json)

This document is short on purpose. Every line is a constraint.

## Hard rules (MUST)

1. **No raw keystrokes on disk.** The edge MUST NOT write raw key event sequences, raw character buffers, or raw chat strings to any persistent storage (filesystem, database, log file, OS pasteboard).
2. **Ring buffer only.** Raw input events MAY exist in an in-process memory ring buffer for the minimum window needed to compute aggregates. The ring buffer MUST be bounded by both size and time, and MUST be cleared on process exit.
3. **Aggregate-only emission.** The only artifacts that cross the edge/core seam are `tempo_point_v0` records validated against [`schemas/tempo_point_v0.schema.json`](../schemas/tempo_point_v0.schema.json). The schema enforces `additionalProperties: false`.
4. **No identifiers.** Tempo points MUST NOT include operator name, machine name, IP, account handle, game username, or any other personally identifying string. The `session_id` is an opaque per-session token (e.g. random UUIDv4) with no derivable link to operator identity.
5. **Game-state coupling stays structural.** Game-state aggregates MAY include numeric or categorical structural facts (unit counts, resource deltas, score, phase) but MUST NOT include free-form text such as chat messages, opponent handles, or in-game communications.
6. **Auditable build.** Any build of the edge that is run against real operator data MUST be reproducible from a tagged commit. Untagged or uncommitted edge builds MUST NOT be pointed at real input streams.

## Permitted aggregates (MAY)

Any of the following, scoped to a single window:

- counts (events, keys, mouse clicks, decisions)
- rates (APM, click-rate, decision-rate)
- intervals (mean / p50 / p95 / max inter-event interval)
- modal categorical summaries (most-used key class such as `movement` / `hotkey` / `modifier`, never the literal key)
- numeric game-state aggregates (unit count, supply, score, resource deltas)
- derived flags (`decision_flag` indicating a window contained a structurally significant decision, without describing the decision content)

## Forbidden fields (MUST NOT)

The schema rejects records containing any of:

- `raw_*` of any kind
- `key_sequence`, `key_events`, `keystroke_log`
- `text`, `chat`, `message_log`, `transcript`
- `username`, `operator_name`, `account_id`, `handle`, `ip_address`, `hostname`

If an emitter needs a field not on the permitted list, the schema MUST be revised forward (`tempo_point_v1`) with explicit review of the new field's redaction implications. The current version MUST NOT be silently extended.

## Audit checklist (before pointing the edge at real input)

- [ ] All persistent writes in the edge codepath go to validated `tempo_point_v0` records, confirmed by grep + test.
- [ ] No log statement or debug print emits raw input characters.
- [ ] Ring buffer has both size and time caps, and a unit test verifies it is cleared on shutdown.
- [ ] Edge build is from a tagged commit.
- [ ] A sample run against synthetic input produces only schema-valid output.

## Failure response

If a violation of any MUST rule is discovered:

1. Halt the edge process immediately.
2. Quarantine any output files produced by the offending build.
3. File a Sandy Chaos pressure event (`kind: workflow-review`, `disposition: KILL` or `REVISE` as appropriate) referencing the violation.
4. Do not resume operator-data capture until the violation has a closed pressure event and a regression test.

## Version

This is `redaction-policy-v0`. Tempo points record the active policy version in their `redaction_version` field so corpus consumers can filter by policy generation.
