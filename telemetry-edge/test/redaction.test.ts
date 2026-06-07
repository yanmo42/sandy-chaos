// Redaction tests.
// These exist to catch any future regression where a forbidden field leaks through the seam.

import { test } from "node:test";
import assert from "node:assert/strict";
import { aggregate, type WindowSpec } from "../src/aggregator.ts";
import { validateTempoPoint, assertValid, TempoPointValidationError } from "../src/schema.ts";
import { openJsonlEmitter } from "../src/emit.ts";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { RawEvent } from "../src/types.ts";

const SPEC: WindowSpec = {
  sessionId: "redaction-test-0001",
  source: "game:sc2",
  windowMs: 30_000,
  pointKind: "apm_window",
  windowEndTs: "2026-06-06T20:00:00-04:00",
};

test("aggregator output never contains raw_* keys, even if attached to inputs", () => {
  // Smuggle attempt: extra property on a RawEvent.
  const tainted = {
    kind: "key",
    ts: 0,
    key_class: "hotkey",
    raw_key: "p",
    chat: "hello",
    typed_text: "password123",
  } as unknown as RawEvent;
  const point = aggregate([tainted], SPEC);
  const serialized = JSON.stringify(point);
  assert.equal(serialized.includes("raw_key"), false);
  assert.equal(serialized.includes("chat"), false);
  assert.equal(serialized.includes("typed_text"), false);
  assert.equal(serialized.includes("password123"), false);
});

test("emit refuses to write a record that includes a raw_keys field", () => {
  const dir = mkdtempSync(join(tmpdir(), "tempo-edge-redaction-"));
  const path = join(dir, "out.jsonl");
  try {
    const e = openJsonlEmitter(path);
    const point = aggregate([], SPEC) as unknown as Record<string, unknown>;
    point["raw_keys"] = ["a", "b"];
    assert.throws(() => e.emit(point as never), TempoPointValidationError);
    const contents = readFileSync(path, "utf-8");
    assert.equal(contents.length, 0, "no record should have been written");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("emit refuses username, chat, hostname, text", () => {
  for (const field of ["username", "chat", "hostname", "text", "transcript", "ip_address"]) {
    const point = aggregate([], SPEC) as unknown as Record<string, unknown>;
    point[field] = "anything";
    assert.throws(() => assertValid(point), TempoPointValidationError, `field ${field} should be rejected`);
  }
});

test("modal_action_class is always a categorical tag from the allowed set", () => {
  const events: RawEvent[] = [
    { kind: "key", ts: 0, key_class: "hotkey", action_class: "engagement" },
    { kind: "key", ts: 1, key_class: "hotkey", action_class: "engagement" },
    { kind: "mouse", ts: 2, button: "primary", action_class: "retreat" },
  ];
  const point = aggregate(events, SPEC);
  const allowed = ["macro", "micro", "control_group", "camera", "build_order", "engagement", "retreat", "idle", "mixed", "none"];
  assert.ok(allowed.includes(point.aggregates.modal_action_class!));
  // Also the record passes the schema (which enforces the same enum).
  assert.equal(validateTempoPoint(point), true);
});
