#!/usr/bin/env node
// CLI: generate a synthetic session, run it through the aggregator+ring buffer, validate each
// emitted record against the schema, and write JSONL to --out.
//
// This is a seam test, not a production capture tool. It uses the synthetic source so the
// run is deterministic and the redaction guarantees are easy to inspect.

import { parseArgs } from "node:util";
import { randomUUID } from "node:crypto";
import { generateSyntheticSession } from "../src/sources/synthetic.ts";
import { RingBuffer } from "../src/ring-buffer.ts";
import { aggregate } from "../src/aggregator.ts";
import { openJsonlEmitter } from "../src/emit.ts";
import type { RawEvent, TempoPointSource } from "../src/types.ts";

const { values } = parseArgs({
  options: {
    out: { type: "string" },
    "duration-ms": { type: "string", default: "180000" },
    "window-ms": { type: "string", default: "30000" },
    "mean-apm": { type: "string", default: "180" },
    seed: { type: "string", default: "1" },
    source: { type: "string", default: "game:sc2" },
  },
});

if (!values.out) {
  console.error("usage: emit-sample.ts --out <path> [--duration-ms N] [--window-ms N] [--mean-apm N] [--seed N] [--source <tag>]");
  process.exit(2);
}

const durationMs = Number(values["duration-ms"]);
const windowMs = Number(values["window-ms"]);
const meanApm = Number(values["mean-apm"]);
const seed = Number(values.seed);
const source = values.source as TempoPointSource;

const sessionStart = Date.now();
const sessionId = randomUUID();
const events = generateSyntheticSession({ durationMs, seed, meanApm });

// Simulated clock tracks the current window end so the ring buffer's time-eviction logic
// behaves the same way it would under live capture.
let simulatedNow = 0;
const ring = new RingBuffer({
  capacity: 50_000,
  retentionMs: windowMs,
  now: () => simulatedNow,
});

const emitter = openJsonlEmitter(values.out);

let windowStart = 0;
let windowEnd = windowMs;
let cursor = 0;

while (windowStart < durationMs) {
  ring.clear();
  simulatedNow = windowEnd;
  while (cursor < events.length && events[cursor]!.ts < windowEnd) {
    const event: RawEvent = events[cursor]!;
    if (event.ts >= windowStart) ring.push(event);
    cursor++;
  }
  const windowEvents = ring.snapshot();
  const windowEndTs = new Date(sessionStart + windowEnd).toISOString();
  const point = aggregate(windowEvents, {
    sessionId,
    source,
    windowMs,
    pointKind: "apm_window",
    windowEndTs,
  });
  emitter.emit(point);
  windowStart += windowMs;
  windowEnd += windowMs;
}

ring.clear();
emitter.close();

console.log(
  `emitted ${emitter.emittedCount()} tempo_point_v0 records to ${values.out} ` +
    `(session ${sessionId}, duration ${durationMs}ms, window ${windowMs}ms, source ${source})`,
);
