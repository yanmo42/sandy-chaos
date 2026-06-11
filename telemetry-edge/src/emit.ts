// Validate-then-write JSONL emission.
//
// Every record passes ajv before it is appended to the output. If validation fails the record
// is rejected (no partial writes, no fallback to "best effort" serialization). This is a hard
// invariant from the redaction policy: nothing that fails the schema gets to disk.

import { appendFileSync, openSync, closeSync } from "node:fs";
import type { TempoPoint } from "./types.ts";
import { assertValid, TempoPointValidationError } from "./schema.ts";

export interface JsonlEmitter {
  emit: (record: TempoPoint) => void;
  close: () => void;
  emittedCount: () => number;
}

export function openJsonlEmitter(path: string): JsonlEmitter {
  const fd = openSync(path, "w");
  closeSync(fd); // truncate
  let count = 0;
  return {
    emit(record) {
      assertValid(record);
      appendFileSync(path, JSON.stringify(record) + "\n", "utf-8");
      count++;
    },
    close() {
      // file is appended per-record; nothing to flush beyond per-write fsync semantics
    },
    emittedCount() {
      return count;
    },
  };
}

export { TempoPointValidationError };
