// In-memory ring buffer for raw input events.
// Contract (see docs/24_tempo_edge_redaction_policy.md):
//   - Size-bounded: capacity events max, oldest dropped on overflow.
//   - Time-bounded: events older than retention_ms are aged out on insert and snapshot.
//   - Never serialized: the buffer is the only place raw events live.
//   - Clearable: clear() empties the buffer; intended to be called on window close and shutdown.
//
// The buffer holds RawEvent items whose categorical tags (key_class, action_class) are already
// safe-for-aggregation by construction. The buffer's job is bounding lifetime and bounding size;
// the upstream capture layer's job is producing tagged events in the first place.

import type { RawEvent } from "./types.ts";

export interface RingBufferOptions {
  capacity: number;
  retentionMs: number;
  now?: () => number;
}

export class RingBuffer {
  private readonly capacity: number;
  private readonly retentionMs: number;
  private readonly now: () => number;
  private items: RawEvent[] = [];

  constructor(opts: RingBufferOptions) {
    if (opts.capacity <= 0) throw new Error("capacity must be > 0");
    if (opts.retentionMs <= 0) throw new Error("retentionMs must be > 0");
    this.capacity = opts.capacity;
    this.retentionMs = opts.retentionMs;
    this.now = opts.now ?? (() => Date.now());
  }

  push(event: RawEvent): void {
    this.evictExpired();
    this.items.push(event);
    if (this.items.length > this.capacity) {
      this.items.splice(0, this.items.length - this.capacity);
    }
  }

  // Snapshot returns the events currently in the buffer, after eviction.
  // The returned array is a copy; mutating it does not affect the buffer.
  snapshot(): RawEvent[] {
    this.evictExpired();
    return this.items.slice();
  }

  size(): number {
    this.evictExpired();
    return this.items.length;
  }

  clear(): void {
    this.items = [];
  }

  private evictExpired(): void {
    const cutoff = this.now() - this.retentionMs;
    let drop = 0;
    while (drop < this.items.length && this.items[drop]!.ts < cutoff) drop++;
    if (drop > 0) this.items.splice(0, drop);
  }
}
