#!/usr/bin/env python3
"""Validate theory-implementation matrix evidence payloads.

`FOUNDATIONS.md` is the source of truth for marker semantics. This module keeps a
small explicit allowlist so validator behavior stays stable if the markdown prose
changes shape.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_FIELDS = (
    "matrix_id",
    "claim_class",
    "markers",
    "files_changed",
    "validation_commands",
    "result_summary",
    "decision",
    "rollback_status",
)

# Canonical marker set from FOUNDATIONS.md §7.
ALLOWED_MARKERS = {
    "O1",
    "O2",
    "O3",
    "N1",
    "N2",
    "N3",
    "I1",
    "I2",
    "I3",
    "C1",
    "C2",
    "C3",
    "C4",
    "P1",
    "P2",
    "P3",
    "E1",
    "E2",
    "E3",
    "E4",
    "E5",
    "A1",
    "A2",
    "A3",
}
HARD_GATE_MARKERS = {"C1", "I1", "P1", "P2"}
ALLOWED_DECISIONS = {"PASS", "REVIEW", "FAIL"}


def _normalize_str_list(raw: object) -> list[str]:
    if isinstance(raw, str):
        parts = [part.strip() for part in raw.replace("\n", ",").split(",")]
        return [part for part in parts if part]
    if isinstance(raw, list):
        out: list[str] = []
        for item in raw:
            text = str(item).strip()
            if text:
                out.append(text)
        return out
    return []


def _missing_required_fields(payload: dict) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if value is None:
            missing.append(field)
            continue
        if isinstance(value, str) and not value.strip():
            missing.append(field)
            continue
        if isinstance(value, list) and not value:
            missing.append(field)
    return missing


def _extract_explicit_violation_markers(payload: dict) -> set[str]:
    markers: set[str] = set()
    for key in ("violated_markers", "hard_gate_violations", "violation_markers"):
        markers.update(_normalize_str_list(payload.get(key)))

    policy_context = payload.get("policy_context")
    if isinstance(policy_context, dict):
        for key in ("violated_markers", "hard_gate_violations", "violation_markers"):
            markers.update(_normalize_str_list(policy_context.get(key)))

    return markers


def validate_evidence_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {
            "decision": "FAIL",
            "ok": False,
            "summary": "Invalid evidence payload: expected JSON object.",
            "errors": ["payload must be a JSON object"],
            "missing_fields": list(REQUIRED_FIELDS),
            "unknown_markers": [],
            "hard_gate_violations": [],
        }

    missing_fields = _missing_required_fields(payload)
    markers = _normalize_str_list(payload.get("markers"))
    known_markers = [marker for marker in markers if marker in ALLOWED_MARKERS]
    unknown_markers = [marker for marker in markers if marker not in ALLOWED_MARKERS]

    explicit_violations = sorted(_extract_explicit_violation_markers(payload) & HARD_GATE_MARKERS)
    declared_decision = str(payload.get("decision", "")).strip().upper()
    errors: list[str] = []
    notes: list[str] = []

    if not markers:
        notes.append("no markers declared")
    if missing_fields:
        errors.append("missing required fields: " + ", ".join(missing_fields))
    if unknown_markers:
        notes.append("unknown markers: " + ", ".join(unknown_markers))
    if declared_decision and declared_decision not in ALLOWED_DECISIONS:
        errors.append(f"invalid decision '{payload.get('decision')}'")
    if explicit_violations:
        errors.append("hard-gate violations: " + ", ".join(explicit_violations))

    if explicit_violations:
        final_decision = "FAIL"
    elif missing_fields or unknown_markers or errors:
        final_decision = "REVIEW"
    elif declared_decision in ALLOWED_DECISIONS:
        final_decision = declared_decision
    else:
        final_decision = "PASS"

    summary_parts = [
        f"matrix_id={str(payload.get('matrix_id', '(missing)')).strip() or '(missing)'}",
        f"decision={final_decision}",
        f"markers={','.join(known_markers) if known_markers else 'none'}",
    ]
    if notes:
        summary_parts.extend(notes)
    if errors:
        summary_parts.extend(errors)

    return {
        "decision": final_decision,
        "ok": final_decision != "FAIL",
        "summary": "; ".join(summary_parts),
        "errors": errors,
        "missing_fields": missing_fields,
        "unknown_markers": unknown_markers,
        "hard_gate_violations": explicit_violations,
        "markers": markers,
        "matrix_id": payload.get("matrix_id"),
    }


def load_payload(source: str | None = None, payload_json: str | None = None) -> dict:
    if payload_json:
        return json.loads(payload_json)
    if not source:
        raise ValueError("payload source required")
    return json.loads(Path(source).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate FOUNDATIONS evidence payloads")
    parser.add_argument("--payload-file", help="Path to JSON evidence payload")
    parser.add_argument("--payload-json", help="Inline JSON evidence payload")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = load_payload(source=args.payload_file, payload_json=args.payload_json)
    result = validate_evidence_payload(payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
