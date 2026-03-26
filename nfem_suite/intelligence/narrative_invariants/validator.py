"""Validation helpers for Symbolic Maps records."""

from __future__ import annotations

from collections.abc import Iterable

from .symbolic_maps import SymbolicOperatorRecord

ALLOWED_CONFIDENCE_TIERS = {"defensible", "plausible", "speculative"}


class ValidationError(ValueError):
    """Raised when a symbolic operator record fails validation."""


def _nonempty_strings(values: Iterable[str], field_name: str) -> list[str]:
    cleaned = [value.strip() for value in values if isinstance(value, str) and value.strip()]
    if not cleaned:
        raise ValidationError(f"{field_name} must contain at least one non-empty string")
    return cleaned


def validate_record(record: SymbolicOperatorRecord) -> None:
    if not record.source_object.strip():
        raise ValidationError("source_object must be non-empty")
    if not record.source_domain.strip():
        raise ValidationError("source_domain must be non-empty")
    if not record.narrative_role.strip():
        raise ValidationError("narrative_role must be non-empty")
    if not record.core_fantasy.strip():
        raise ValidationError("core_fantasy must be non-empty")
    if not record.constraint_pattern.strip():
        raise ValidationError("constraint_pattern must be non-empty")

    _nonempty_strings(record.signature_operators, "signature_operators")
    _nonempty_strings(record.failure_modes, "failure_modes")

    if record.confidence_tier not in ALLOWED_CONFIDENCE_TIERS:
        raise ValidationError(
            f"confidence_tier must be one of {sorted(ALLOWED_CONFIDENCE_TIERS)}"
        )


def validate_records(records: Iterable[SymbolicOperatorRecord]) -> None:
    seen = set()
    for record in records:
        validate_record(record)
        key = (record.source_object.lower(), record.source_domain.lower())
        if key in seen:
            raise ValidationError(
                f"duplicate symbolic record for {record.source_object!r} in {record.source_domain!r}"
            )
        seen.add(key)
