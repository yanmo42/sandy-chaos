// Synthetic event source.
//
// Produces deterministic RawEvent streams that mimic what a real SC2 replay parser + input
// listener would emit. Deterministic = seeded PRNG, no Date.now(). Used by tests and by the
// emit-sample CLI to demonstrate the seam end-to-end without depending on a real game-state
// parser or input capture.
//
// This source NEVER produces raw text, raw key codes, or operator identifiers. Events carry
// only the categorical/structural fields that the production capture layer is also expected
// to produce.

import type { RawEvent, KeyClass, ActionClass, Phase, DecisionFlagKind } from "../types.ts";

function mulberry32(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export interface SyntheticSessionOptions {
  durationMs: number;
  seed?: number;
  meanApm?: number; // target APM
  clickFraction?: number; // share of input events that are clicks (0..1)
}

const KEY_CLASS_POOL: KeyClass[] = ["movement", "hotkey", "modifier"];
const ACTION_CLASS_POOL: ActionClass[] = [
  "macro",
  "micro",
  "control_group",
  "camera",
  "build_order",
  "engagement",
  "retreat",
];
const DECISION_KIND_POOL: DecisionFlagKind[] = [
  "build_order_change",
  "engagement_initiated",
  "engagement_disengaged",
  "expansion",
  "tech_switch",
  "scout_dispatch",
];
const PHASE_ORDER: Phase[] = ["opening", "early", "mid", "late", "endgame"];

export function generateSyntheticSession(opts: SyntheticSessionOptions): RawEvent[] {
  const seed = opts.seed ?? 1;
  const rng = mulberry32(seed);
  const meanApm = opts.meanApm ?? 150;
  const clickFraction = opts.clickFraction ?? 0.25;
  const totalSeconds = opts.durationMs / 1000;
  const expectedInputs = (meanApm / 60) * totalSeconds;

  const events: RawEvent[] = [];

  // Input events: Poisson-ish placement via uniform draws + sort, then label.
  for (let i = 0; i < expectedInputs; i++) {
    const ts = Math.floor(rng() * opts.durationMs);
    const isClick = rng() < clickFraction;
    const actionClass = ACTION_CLASS_POOL[Math.floor(rng() * ACTION_CLASS_POOL.length)]!;
    if (isClick) {
      events.push({
        kind: "mouse",
        ts,
        button: rng() < 0.85 ? "primary" : "secondary",
        action_class: actionClass,
      });
    } else {
      const keyClass = KEY_CLASS_POOL[Math.floor(rng() * KEY_CLASS_POOL.length)]!;
      events.push({
        kind: "key",
        ts,
        key_class: keyClass,
        action_class: actionClass,
      });
    }
  }

  // Decisions: 1 per ~5s of session, structurally tagged.
  const decisionCount = Math.max(1, Math.floor(totalSeconds / 5));
  for (let i = 0; i < decisionCount; i++) {
    const ts = Math.floor(rng() * opts.durationMs);
    events.push({
      kind: "decision",
      ts,
      decision_flag_kind: DECISION_KIND_POOL[Math.floor(rng() * DECISION_KIND_POOL.length)]!,
    });
  }

  // Game state: phase transitions + periodic supply/resource ticks.
  const gameStateTickMs = 30_000;
  for (let t = 0; t < opts.durationMs; t += gameStateTickMs) {
    const phaseIdx = Math.min(PHASE_ORDER.length - 1, Math.floor((t / opts.durationMs) * PHASE_ORDER.length));
    events.push({
      kind: "game_state",
      ts: t,
      delta: {
        phase: PHASE_ORDER[phaseIdx]!,
        supply_delta: Math.floor((rng() - 0.5) * 10),
        resource_delta_primary: Math.floor(rng() * 200 - 50),
        resource_delta_secondary: Math.floor(rng() * 100 - 25),
        unit_count_delta: Math.floor((rng() - 0.5) * 6),
        engagement_flag: rng() < 0.2,
      },
    });
  }

  events.sort((a, b) => a.ts - b.ts);
  return events;
}
