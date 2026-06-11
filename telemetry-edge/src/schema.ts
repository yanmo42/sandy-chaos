import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const HERE = dirname(fileURLToPath(import.meta.url));
const SCHEMA_PATH = resolve(HERE, "../../schemas/tempo_point_v0.schema.json");

export const tempoPointSchema = JSON.parse(
  readFileSync(SCHEMA_PATH, "utf-8"),
) as Record<string, unknown>;

// strictRequired is disabled because the schema uses `required` inside a `not/anyOf` block
// to declare forbidden fields. Those fields are intentionally NOT in `properties` (we want
// the schema to be silent about them at the type level while explicitly rejecting them).
// All other ajv strict checks remain on.
const ajv = new Ajv2020({ allErrors: true, strict: true, strictRequired: false });
addFormats(ajv);

export const validateTempoPoint = ajv.compile(tempoPointSchema);

export class TempoPointValidationError extends Error {
  readonly errors: ReturnType<typeof validateTempoPoint>;
  readonly record: unknown;
  constructor(
    message: string,
    errors: ReturnType<typeof validateTempoPoint>,
    record: unknown,
  ) {
    super(message);
    this.name = "TempoPointValidationError";
    this.errors = errors;
    this.record = record;
  }
}

export function assertValid(record: unknown): asserts record {
  if (!validateTempoPoint(record)) {
    throw new TempoPointValidationError(
      "tempo_point_v0 validation failed: " +
        JSON.stringify(validateTempoPoint.errors),
      validateTempoPoint.errors,
      record,
    );
  }
}
