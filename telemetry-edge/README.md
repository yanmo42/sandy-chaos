# @sandy-chaos/telemetry-edge

The self-referential tempo edge for the Sandy Chaos research engine.

**Status:** Medium scope (synthetic source + aggregator + validated emission). No live capture yet.

## What it does

Reads streams of operator input and game-state events, aggregates them into windows, and emits `tempo_point_v0` records (one JSON object per window) for the Python research core to consume.

**Architecturally enforced redaction:** raw input events live only in an in-memory ring buffer. The aggregator's output type physically cannot contain raw key sequences, chat strings, or operator identifiers. The schema's `additionalProperties: false` and top-level `not` block enforce the same constraint at the wire boundary. See [`../docs/24_tempo_edge_redaction_policy.md`](../docs/24_tempo_edge_redaction_policy.md).

## Layout

```
src/
  types.ts          TS types mirroring tempo_point_v0
  schema.ts         schema loader + ajv validator
  ring-buffer.ts    size+time bounded buffer, clear-on-shutdown
  aggregator.ts     event stream -> windowed tempo_point
  emit.ts           validate-then-write JSONL
  sources/
    synthetic.ts    synthetic event generator (for tests and demo)
bin/
  emit-sample.ts    CLI: generate synthetic session, emit JSONL
test/
  schema.test.ts
  ring-buffer.test.ts
  aggregator.test.ts
  redaction.test.ts
  integration.test.ts
```

## Usage

```bash
cd telemetry-edge
npm install
npm test
npm run emit-sample -- --out /tmp/sample.jsonl
```

The CLI generates a synthetic session, runs it through the aggregator, validates each emitted record against the schema, and writes JSONL to `--out`.

## Non-goals (for this scope)

- No real SC2 replay parser. The seam is proven against synthetic input.
- No keyboard/mouse capture. Real input is a separate later scope, gated on operator review.
- No npm publication. This package is `private: true`.
- No live session capture. Bin/emit-sample is for testing the seam, not for production use.
