// Window aggregator: RawEvent stream -> TempoPoint window summaries.
//
// Redaction-by-construction: this module reads only the categorical/structural fields of
// RawEvent (kind, key_class, action_class, decision_flag_kind, game-state numerics). It does
// not touch any field that could carry verbatim user input — there is no such field on RawEvent
// in the first place. Even if a malicious upstream attached an extra property to a RawEvent,
// the aggregator's output type (TempoAggregates) physically cannot carry it, and the schema
// validator at emit time would reject any record that did.

import type {
  RawEvent,
  TempoPoint,
  TempoAggregates,
  TempoPointSource,
  PointKind,
  KeyClass,
  ActionClass,
  GameStateAggregates,
} from "./types.ts";

export interface WindowSpec {
  sessionId: string;
  source: TempoPointSource;
  windowMs: number;
  pointKind: PointKind;
  windowEndTs: string; // ISO-8601 timestamp marking window END
}

function percentile(sorted: number[], p: number): number {
  if (sorted.length === 0) return 0;
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.floor(p * sorted.length)));
  return sorted[idx]!;
}

function mean(values: number[]): number {
  if (values.length === 0) return 0;
  let s = 0;
  for (const v of values) s += v;
  return s / values.length;
}

function modal<T extends string>(counts: Map<T, number>, fallback: T): T {
  let best: T = fallback;
  let bestCount = -1;
  let total = 0;
  for (const [k, v] of counts) {
    total += v;
    if (v > bestCount) {
      best = k;
      bestCount = v;
    }
  }
  if (total === 0) return fallback;
  return best;
}

function intervalsBetween(timestamps: number[]): number[] {
  if (timestamps.length < 2) return [];
  const sorted = timestamps.slice().sort((a, b) => a - b);
  const out: number[] = [];
  for (let i = 1; i < sorted.length; i++) {
    out.push(sorted[i]! - sorted[i - 1]!);
  }
  return out;
}

function sumGameState(events: RawEvent[]): GameStateAggregates | undefined {
  const gs = events.flatMap((e) => (e.kind === "game_state" ? [e] : []));
  if (gs.length === 0) return undefined;
  const out: GameStateAggregates = {};
  let any = false;
  const add = (field: keyof GameStateAggregates, v: number | undefined) => {
    if (v === undefined) return;
    any = true;
    if (typeof out[field] === "number") {
      (out[field] as number) += v;
    } else {
      (out[field] as number) = v;
    }
  };
  for (const e of gs) {
    add("unit_count_delta", e.delta.unit_count_delta);
    add("supply_delta", e.delta.supply_delta);
    add("resource_delta_primary", e.delta.resource_delta_primary);
    add("resource_delta_secondary", e.delta.resource_delta_secondary);
    add("score_delta", e.delta.score_delta);
    if (e.delta.phase !== undefined) {
      out.phase = e.delta.phase;
      any = true;
    }
    if (e.delta.engagement_flag !== undefined) {
      out.engagement_flag = e.delta.engagement_flag;
      any = true;
    }
  }
  return any ? out : undefined;
}

export function aggregate(events: RawEvent[], spec: WindowSpec): TempoPoint {
  const keyEvents = events.filter((e) => e.kind === "key");
  const mouseEvents = events.filter((e) => e.kind === "mouse");
  const decisionEvents = events.filter((e) => e.kind === "decision");

  const inputEventCount = keyEvents.length + mouseEvents.length;
  const allInputTs = [
    ...keyEvents.map((e) => e.ts),
    ...mouseEvents.map((e) => e.ts),
  ];
  const intervals = intervalsBetween(allInputTs);
  const intervalsSorted = intervals.slice().sort((a, b) => a - b);

  const windowSeconds = spec.windowMs / 1000;
  const apm = windowSeconds > 0 ? (keyEvents.length / windowSeconds) * 60 : 0;
  const clickRate = windowSeconds > 0 ? mouseEvents.length / windowSeconds : 0;
  const decisionRate = windowSeconds > 0 ? decisionEvents.length / windowSeconds : 0;

  const keyClassCounts = new Map<KeyClass, number>();
  for (const e of keyEvents) {
    keyClassCounts.set(e.key_class, (keyClassCounts.get(e.key_class) ?? 0) + 1);
  }
  for (const e of mouseEvents) {
    const cls: KeyClass = e.button === "primary" ? "mouse_primary" : "mouse_secondary";
    keyClassCounts.set(cls, (keyClassCounts.get(cls) ?? 0) + 1);
  }

  const actionClassCounts = new Map<ActionClass, number>();
  for (const e of [...keyEvents, ...mouseEvents]) {
    if (e.action_class) {
      actionClassCounts.set(e.action_class, (actionClassCounts.get(e.action_class) ?? 0) + 1);
    }
  }

  const aggregates: TempoAggregates = {
    event_count: inputEventCount + decisionEvents.length,
    key_count: keyEvents.length,
    click_count: mouseEvents.length,
    decision_count: decisionEvents.length,
    apm,
    click_rate_hz: clickRate,
    decision_rate_hz: decisionRate,
  };

  if (intervals.length > 0) {
    aggregates.inter_event_interval_ms_mean = mean(intervals);
    aggregates.inter_event_interval_ms_p50 = percentile(intervalsSorted, 0.5);
    aggregates.inter_event_interval_ms_p95 = percentile(intervalsSorted, 0.95);
    aggregates.inter_event_interval_ms_max = intervalsSorted[intervalsSorted.length - 1]!;
  }

  if (inputEventCount > 0) {
    aggregates.modal_key_class = modal(keyClassCounts, "none");
  } else {
    aggregates.modal_key_class = "none";
  }
  if (actionClassCounts.size > 0) {
    aggregates.modal_action_class = modal(actionClassCounts, "none");
  } else {
    aggregates.modal_action_class = "none";
  }

  const gameState = sumGameState(events);
  if (gameState) aggregates.game_state = gameState;

  if (decisionEvents.length > 0) {
    aggregates.decision_flag_kind = decisionEvents[0]!.decision_flag_kind;
  }

  return {
    schema_version: "tempo_point/v0",
    ts: spec.windowEndTs,
    session_id: spec.sessionId,
    source: spec.source,
    window_ms: spec.windowMs,
    point_kind: spec.pointKind,
    aggregates,
    redaction_version: "redaction-policy-v0",
  };
}
