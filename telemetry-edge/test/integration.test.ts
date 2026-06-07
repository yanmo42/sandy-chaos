// End-to-end seam test: synthetic source -> ring buffer -> aggregator -> emit -> validate.

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { generateSyntheticSession } from "../src/sources/synthetic.ts";
import { RingBuffer } from "../src/ring-buffer.ts";
import { aggregate } from "../src/aggregator.ts";
import { openJsonlEmitter } from "../src/emit.ts";
import { validateTempoPoint } from "../src/schema.ts";

test("synthetic session round-trip produces validated JSONL records", () => {
  const dir = mkdtempSync(join(tmpdir(), "tempo-edge-integration-"));
  const path = join(dir, "out.jsonl");
  try {
    const durationMs = 120_000;
    const windowMs = 30_000;
    const events = generateSyntheticSession({ durationMs, seed: 42, meanApm: 180 });

    let simulatedNow = 0;
    const ring = new RingBuffer({
      capacity: 10_000,
      retentionMs: windowMs,
      now: () => simulatedNow,
    });
    const emitter = openJsonlEmitter(path);
    const sessionId = randomUUID();

    let windowStart = 0;
    let windowEnd = windowMs;
    let cursor = 0;
    const expectedWindows = durationMs / windowMs;
    let maxApmSeen = 0;

    while (windowStart < durationMs) {
      ring.clear();
      simulatedNow = windowEnd;
      while (cursor < events.length && events[cursor]!.ts < windowEnd) {
        const event = events[cursor]!;
        if (event.ts >= windowStart) ring.push(event);
        cursor++;
      }
      const windowEvents = ring.snapshot();
      const point = aggregate(windowEvents, {
        sessionId,
        source: "game:sc2",
        windowMs,
        pointKind: "apm_window",
        windowEndTs: new Date(windowEnd).toISOString(),
      });
      emitter.emit(point);
      if ((point.aggregates.apm ?? 0) > maxApmSeen) maxApmSeen = point.aggregates.apm!;
      windowStart += windowMs;
      windowEnd += windowMs;
    }

    ring.clear();
    emitter.close();
    assert.equal(emitter.emittedCount(), expectedWindows);
    assert.ok(maxApmSeen > 50, `expected at least one window with apm > 50, got max ${maxApmSeen}`);

    const lines = readFileSync(path, "utf-8").trim().split("\n");
    assert.equal(lines.length, expectedWindows);
    for (const line of lines) {
      const obj = JSON.parse(line);
      assert.equal(validateTempoPoint(obj), true);
    }

    // Defense in depth: the JSONL must not contain any forbidden token.
    const text = readFileSync(path, "utf-8");
    for (const forbidden of ["raw_keys", "raw_input", "chat", "transcript", "username", "hostname", "password"]) {
      assert.equal(text.includes(forbidden), false, `JSONL must not contain '${forbidden}'`);
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
