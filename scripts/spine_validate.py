#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from typing import Any
import sys

from scripts import spine_common


def _loc(item: spine_common.LoadedItem) -> str:
    try:
        rel = item.path.relative_to(spine_common.ROOT)
    except ValueError:
        rel = item.path
    if item.line is not None:
        return f"{rel}:line {item.line}"
    return str(rel)


def _require_fields(item: spine_common.LoadedItem, required: set[str], errors: list[str]) -> None:
    missing = sorted(field for field in required if field not in item.data)
    if missing:
        errors.append(f"{_loc(item)}: missing required field(s): {', '.join(missing)}")


def _require_non_empty_string(item: spine_common.LoadedItem, field: str, errors: list[str]) -> None:
    value = item.data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{_loc(item)}: field '{field}' must be a non-empty string")


def _require_list(item: spine_common.LoadedItem, field: str, errors: list[str], min_items: int = 0) -> None:
    value = item.data.get(field)
    if not isinstance(value, list):
        errors.append(f"{_loc(item)}: field '{field}' must be a list")
        return
    if len(value) < min_items:
        errors.append(f"{_loc(item)}: field '{field}' must contain at least {min_items} item(s)")


def _require_enum(item: spine_common.LoadedItem, field: str, allowed: set[str], errors: list[str]) -> None:
    value = item.data.get(field)
    if value not in allowed:
        errors.append(f"{_loc(item)}: invalid {field} '{value}'")


def _check_id(item: spine_common.LoadedItem, field: str, regex, errors: list[str]) -> str | None:
    value = item.data.get(field)
    if not isinstance(value, str) or not regex.match(value):
        errors.append(f"{_loc(item)}: invalid {field} '{value}'")
        return None
    return value


def _check_duplicate_ids(seen: dict[str, str], identifier: str, location: str, errors: list[str]) -> None:
    prior = seen.get(identifier)
    if prior:
        errors.append(f"{location}: duplicate id '{identifier}' (already seen at {prior})")
    else:
        seen[identifier] = location


def validate_concepts(concepts: list[spine_common.LoadedItem], errors: list[str], warnings: list[str]) -> set[str]:
    seen: dict[str, str] = {}
    concept_ids: set[str] = set()

    for item in concepts:
        _require_fields(item, spine_common.CONCEPT_REQUIRED, errors)
        identifier = _check_id(item, "id", spine_common.CONCEPT_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            concept_ids.add(identifier)

        _require_non_empty_string(item, "name", errors)
        _require_non_empty_string(item, "summary", errors)
        _require_non_empty_string(item, "next_action", errors)
        _require_enum(item, "lane", spine_common.ALLOWED_LANES, errors)
        _require_enum(item, "claim_tier", spine_common.ALLOWED_TIERS, errors)
        _require_enum(item, "status", spine_common.ALLOWED_STATUS, errors)
        _require_enum(item, "promotion_target", spine_common.ALLOWED_PROMOTION_TARGETS, errors)
        _require_enum(item, "owner_surface", spine_common.ALLOWED_OWNER_SURFACES, errors)

        for field in ("depends_on", "documented_in", "implemented_in", "tested_by", "contradicts", "failure_conditions"):
            _require_list(item, field, errors, min_items=1 if field == "failure_conditions" else 0)

        if "missing_assumptions" in item.data:
            _require_list(item, "missing_assumptions", errors, min_items=0)

        if item.data.get("next_test") is not None:
            _require_non_empty_string(item, "next_test", errors)

        if item.data.get("status") == "canonical" and not item.data.get("documented_in"):
            warnings.append(f"{_loc(item)}: canonical concept has no documented_in links")
        if not item.data.get("tested_by"):
            warnings.append(f"{_loc(item)}: concept has no tested_by links")
        if item.data.get("status") in {"draft", "pressure-testing", "validated-partial"} and not item.data.get("next_test"):
            warnings.append(f"{_loc(item)}: active concept has no next_test field")
        if item.data.get("owner_surface") == "ygg-candidate" and not str(item.data.get("promotion_target", "")).startswith("ygg"):
            warnings.append(f"{_loc(item)}: ygg-candidate should usually target a Ygg promotion surface")

    return concept_ids


def validate_concept_references(concepts: list[spine_common.LoadedItem], concept_ids: set[str], errors: list[str]) -> None:
    for item in concepts:
        for field in ("depends_on", "contradicts"):
            for ref in item.data.get(field, []):
                if ref not in concept_ids:
                    errors.append(f"{_loc(item)}: {field} references missing concept '{ref}'")


def validate_pressure_events(events: list[spine_common.LoadedItem], concept_ids: set[str], errors: list[str], warnings: list[str]) -> set[str]:
    seen: dict[str, str] = {}
    event_ids: set[str] = set()

    for item in events:
        _require_fields(item, spine_common.PRESSURE_REQUIRED, errors)
        identifier = _check_id(item, "id", spine_common.PRESSURE_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            event_ids.add(identifier)

        date = item.data.get("date")
        if not isinstance(date, str) or not spine_common.DATE_RE.match(date):
            errors.append(f"{_loc(item)}: invalid date '{date}'")

        _require_non_empty_string(item, "summary", errors)
        _require_non_empty_string(item, "next_action", errors)
        _require_enum(item, "kind", spine_common.ALLOWED_PRESSURE_KINDS, errors)
        _require_enum(item, "result", spine_common.ALLOWED_PRESSURE_RESULTS, errors)
        _require_enum(item, "disposition", spine_common.ALLOWED_PRESSURE_DISPOSITIONS, errors)
        _require_list(item, "concepts", errors, min_items=1)
        _require_list(item, "evidence", errors, min_items=1)

        for ref in item.data.get("concepts", []):
            if ref not in concept_ids:
                errors.append(f"{_loc(item)}: references missing concept '{ref}'")
        if item.data.get("result") == "support" and item.data.get("disposition") == "WAITING_ON_EVIDENCE":
            warnings.append(f"{_loc(item)}: support result paired with WAITING_ON_EVIDENCE looks inconsistent")

    return event_ids


def validate_promotion_events(events: list[spine_common.LoadedItem], concept_ids: set[str], errors: list[str], warnings: list[str]) -> set[str]:
    seen: dict[str, str] = {}
    event_ids: set[str] = set()

    for item in events:
        if "__parse_error__" in item.data:
            errors.append(f"{_loc(item)}: {item.data['__parse_error__']}")
            continue

        _require_fields(item, spine_common.PROMOTION_REQUIRED, errors)
        identifier = _check_id(item, "id", spine_common.PROMOTION_ID_RE, errors)
        if identifier:
            _check_duplicate_ids(seen, identifier, _loc(item), errors)
            event_ids.add(identifier)

        date = item.data.get("date")
        if not isinstance(date, str) or not spine_common.DATE_RE.match(date):
            errors.append(f"{_loc(item)}: invalid date '{date}'")

        _require_non_empty_string(item, "basis", errors)
        _require_enum(item, "from_status", spine_common.ALLOWED_STATUS, errors)
        _require_enum(item, "to_status", spine_common.ALLOWED_STATUS, errors)
        _require_enum(item, "promotion_target", spine_common.ALLOWED_PROMOTION_TARGETS, errors)
        _require_enum(item, "disposition", spine_common.ALLOWED_PROMOTION_DISPOSITIONS, errors)
        _require_list(item, "concepts", errors, min_items=1)

        for ref in item.data.get("concepts", []):
            if ref not in concept_ids:
                errors.append(f"{_loc(item)}: references missing concept '{ref}'")
        if item.data.get("from_status") == item.data.get("to_status"):
            warnings.append(f"{_loc(item)}: from_status and to_status are identical")

    return event_ids


def build_warning_index(events: list[spine_common.LoadedItem], field: str) -> dict[str, list[spine_common.LoadedItem]]:
    index: dict[str, list[spine_common.LoadedItem]] = defaultdict(list)
    for item in events:
        for ref in item.data.get(field, []):
            index[ref].append(item)
    return index


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    concepts = spine_common.load_concepts()
    pressure_events = spine_common.load_pressure_events()
    promotion_events = spine_common.load_promotion_events()

    concept_ids = validate_concepts(concepts, errors, warnings)
    validate_concept_references(concepts, concept_ids, errors)
    validate_pressure_events(pressure_events, concept_ids, errors, warnings)
    validate_promotion_events(promotion_events, concept_ids, errors, warnings)

    pressure_by_concept = build_warning_index(pressure_events, "concepts")
    for item in concepts:
        concept_id = item.data.get("id")
        if concept_id and concept_id not in pressure_by_concept:
            warnings.append(f"{_loc(item)}: concept has no linked pressure events")

    if errors:
        print("Spine validation failed.")
        print()
        print("ERRORS")
        for err in errors:
            print(f"- {err}")
        if warnings:
            print()
            print("WARNINGS")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    print("Spine validation passed.")
    print(f"- {len(concepts)} concepts")
    print(f"- {len(pressure_events)} pressure events")
    print(f"- {len(promotion_events)} promotion events")
    print(f"- {len(errors)} errors")
    print(f"- {len(warnings)} warnings")
    if warnings:
        print()
        print("WARNINGS")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
