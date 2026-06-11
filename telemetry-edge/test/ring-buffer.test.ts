import { test } from "node:test";
import assert from "node:assert/strict";
import { RingBuffer } from "../src/ring-buffer.ts";
import type { RawKeyEvent } from "../src/types.ts";

function key(ts: number): RawKeyEvent {
  return { kind: "key", ts, key_class: "hotkey" };
}

test("size cap drops oldest on overflow", () => {
  let now = 0;
  const buf = new RingBuffer({ capacity: 3, retentionMs: 1_000_000, now: () => now });
  for (let i = 0; i < 5; i++) buf.push(key(i));
  assert.equal(buf.size(), 3);
  const items = buf.snapshot();
  assert.deepEqual(items.map((e) => (e as RawKeyEvent).ts), [2, 3, 4]);
});

test("time cap evicts events older than retentionMs", () => {
  let now = 100;
  const buf = new RingBuffer({ capacity: 100, retentionMs: 50, now: () => now });
  buf.push(key(10));
  buf.push(key(60));
  buf.push(key(95));
  now = 200;
  assert.equal(buf.size(), 0); // all older than now-50=150
  now = 100;
  buf.push(key(60));
  buf.push(key(80));
  now = 120;
  assert.equal(buf.size(), 1); // only the ts=80 event survives (cutoff = 120-50 = 70)
});

test("clear empties the buffer", () => {
  let now = 0;
  const buf = new RingBuffer({ capacity: 10, retentionMs: 1000, now: () => now });
  buf.push(key(1));
  buf.push(key(2));
  assert.equal(buf.size(), 2);
  buf.clear();
  assert.equal(buf.size(), 0);
  assert.deepEqual(buf.snapshot(), []);
});

test("snapshot returns a copy, not the live array", () => {
  let now = 0;
  const buf = new RingBuffer({ capacity: 10, retentionMs: 1000, now: () => now });
  buf.push(key(1));
  const snap = buf.snapshot();
  snap.length = 0; // mutate the copy
  assert.equal(buf.size(), 1); // buffer untouched
});

test("constructor rejects invalid bounds", () => {
  assert.throws(() => new RingBuffer({ capacity: 0, retentionMs: 100 }));
  assert.throws(() => new RingBuffer({ capacity: 5, retentionMs: 0 }));
});
