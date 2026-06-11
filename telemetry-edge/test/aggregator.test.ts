import { test } from "node:test";
import assert from "node:assert/strict";
import { aggregate, type WindowSpec } from "../src/aggregator.ts";
import { validateTempoPoint } from "../src/schema.ts";
import type { RawEvent } from "../src/types.ts";

const SPEC: WindowSpec = {
  sessionId: "agg-test-0001",
  source: "game:sc2",
  windowMs: 60_000,
  pointKind: "apm_window",
  windowEndTs: "2026-06-06T20:00:00-04:00",
};

test("empty window emits a zero-count, schema-valid record", () => {
  const point = aggregate([], SPEC);
  assert.equal(validateTempoPoint(point), true);
  assert.equal(point.aggregates.event_count, 0);
  assert.equal(point.aggregates.key_count, 0);
  assert.equal(point.aggregates.apm, 0);
  assert.equal(point.aggregates.modal_key_class, "none");
});

test("APM = key_count * 60 / window_seconds", () => {
  const events: RawEvent[] = [];
  for (let i = 0; i < 180; i++) {
    events.push({ kind: "key", ts: i * 333, key_class: "hotkey" });
  }
  const point = aggregate(events, SPEC); // 60s window
  assert.equal(point.aggregates.key_count, 180);
  assert.equal(point.aggregates.apm, 180); // 180 keys per 60s = 180 APM
});

test("modal_key_class returns the most common class, never a literal key", () => {
  const events: RawEvent[] = [
    { kind: "key", ts: 1, key_class: "movement" },
    { kind: "key", ts: 2, key_class: "movement" },
    { kind: "key", ts: 3, key_class: "movement" },
    { kind: "key", ts: 4, key_class: "hotkey" },
    { kind: "key", ts: 5, key_class: "modifier" },
  ];
  const point = aggregate(events, SPEC);
  assert.equal(point.aggregates.modal_key_class, "movement");
  // The output is a categorical tag, not anything that could contain a key character.
  assert.ok(
    ["movement", "hotkey", "modifier", "mouse_primary", "mouse_secondary", "mixed", "none"].includes(
      point.aggregates.modal_key_class!,
    ),
  );
});

test("intervals: mean/p50/p95/max computed only when there are 2+ events", () => {
  const events: RawEvent[] = [
    { kind: "key", ts: 0, key_class: "hotkey" },
    { kind: "key", ts: 100, key_class: "hotkey" },
    { kind: "key", ts: 200, key_class: "hotkey" },
    { kind: "key", ts: 350, key_class: "hotkey" },
  ];
  const point = aggregate(events, SPEC);
  // intervals = [100, 100, 150], sorted = [100, 100, 150]
  assert.equal(point.aggregates.inter_event_interval_ms_max, 150);
  assert.equal(point.aggregates.inter_event_interval_ms_p50, 100);
  assert.equal(point.aggregates.inter_event_interval_ms_mean, 350 / 3);
});

test("intervals absent on single-event window", () => {
  const events: RawEvent[] = [{ kind: "key", ts: 0, key_class: "hotkey" }];
  const point = aggregate(events, SPEC);
  assert.equal(point.aggregates.inter_event_interval_ms_mean, undefined);
});

test("game_state aggregates sum numeric deltas", () => {
  const events: RawEvent[] = [
    { kind: "game_state", ts: 0, delta: { phase: "opening", supply_delta: 5 } },
    { kind: "game_state", ts: 100, delta: { supply_delta: 3, resource_delta_primary: 100 } },
  ];
  const point = aggregate(events, SPEC);
  assert.equal(point.aggregates.game_state?.supply_delta, 8);
  assert.equal(point.aggregates.game_state?.resource_delta_primary, 100);
  assert.equal(point.aggregates.game_state?.phase, "opening");
});

test("decision events contribute to decision_count and decision_flag_kind", () => {
  const events: RawEvent[] = [
    { kind: "decision", ts: 100, decision_flag_kind: "engagement_initiated" },
  ];
  const point = aggregate(events, SPEC);
  assert.equal(point.aggregates.decision_count, 1);
  assert.equal(point.aggregates.decision_flag_kind, "engagement_initiated");
});

test("aggregate output is always schema-valid (mixed event stream)", () => {
  const events: RawEvent[] = [
    { kind: "key", ts: 0, key_class: "hotkey", action_class: "micro" },
    { kind: "mouse", ts: 50, button: "primary", action_class: "engagement" },
    { kind: "decision", ts: 75, decision_flag_kind: "engagement_initiated" },
    { kind: "game_state", ts: 100, delta: { phase: "mid", engagement_flag: true } },
  ];
  const point = aggregate(events, SPEC);
  assert.equal(validateTempoPoint(point), true);
});
