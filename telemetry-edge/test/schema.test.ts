import { test } from "node:test";
import assert from "node:assert/strict";
import { validateTempoPoint, tempoPointSchema, assertValid, TempoPointValidationError } from "../src/schema.ts";

const VALID: Record<string, unknown> = {
  schema_version: "tempo_point/v0",
  ts: "2026-06-06T20:00:00-04:00",
  session_id: "test-session-0001",
  source: "game:sc2",
  window_ms: 30000,
  point_kind: "apm_window",
  aggregates: {
    event_count: 100,
    key_count: 80,
    click_count: 20,
    apm: 160,
    modal_key_class: "hotkey",
    modal_action_class: "micro",
  },
  redaction_version: "redaction-policy-v0",
};

test("schema is loaded with the expected $id", () => {
  assert.equal(
    tempoPointSchema["$id"],
    "https://github.com/yanmo42/sandy-chaos/schemas/tempo_point_v0.schema.json",
  );
});

test("valid record passes", () => {
  assert.equal(validateTempoPoint(VALID), true);
});

test("raw_keys is rejected", () => {
  const bad = { ...VALID, raw_keys: ["a", "s", "d"] };
  assert.equal(validateTempoPoint(bad), false);
});

test("username is rejected", () => {
  const bad = { ...VALID, username: "ian" };
  assert.equal(validateTempoPoint(bad), false);
});

test("unknown root field is rejected (additionalProperties)", () => {
  const bad = { ...VALID, mystery_field: 42 };
  assert.equal(validateTempoPoint(bad), false);
});

test("unknown aggregate field is rejected (additionalProperties)", () => {
  const bad = {
    ...VALID,
    aggregates: { ...(VALID.aggregates as object), secret_typed_text: "hello" },
  };
  assert.equal(validateTempoPoint(bad), false);
});

test("window_ms upper bound enforced", () => {
  const bad = { ...VALID, window_ms: 999_999_999 };
  assert.equal(validateTempoPoint(bad), false);
});

test("schema_version const enforced", () => {
  const bad = { ...VALID, schema_version: "tempo_point/v1" };
  assert.equal(validateTempoPoint(bad), false);
});

test("redaction_version const enforced", () => {
  const bad = { ...VALID, redaction_version: "redaction-policy-v1" };
  assert.equal(validateTempoPoint(bad), false);
});

test("assertValid throws TempoPointValidationError on bad record", () => {
  assert.throws(
    () => assertValid({ ...VALID, raw_keys: ["x"] }),
    TempoPointValidationError,
  );
});
