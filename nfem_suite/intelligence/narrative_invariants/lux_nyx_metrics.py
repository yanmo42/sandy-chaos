"""Lux–Nyx pilot measurement counters and baseline reports.

This module is intentionally small and deterministic. It records only causal
operator events that happened in the current workflow: suggestions surfaced,
accepted suggestions, correction burden, archive items observed, and archive
items later promoted. Baseline comparison is explicit and opt-in so provisional
pilot data cannot claim lift against a synthetic zero baseline.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HEADLINE_METRIC_KEYS: tuple[str, ...] = (
    "suggestion_acceptance_rate",
    "correction_burden_per_suggestion",
    "archive_to_promotion_conversion_quality",
)

# Small enough to be useful in this repo, large enough to flag tiny-n reads as
# provisional. The report exposes remaining samples per metric.
MIN_PILOT_SAMPLE_SIZE = 10
MIN_RESOLUTION_COVERAGE = 0.80

PROMOTION_VERDICTS: tuple[str, ...] = (
    "invalid-counters",
    "baseline-unconfigured",
    "insufficient-samples",
    "insufficient-resolution",
    "worse",
    "no-lift",
    "promote-candidate",
)

_HIGHER_IS_BETTER = {
    "suggestion_acceptance_rate": True,
    "correction_burden_per_suggestion": False,
    "archive_to_promotion_conversion_quality": True,
}


def _state_dir(root: str | Path) -> Path:
    return Path(root) / "state" / "lux_nyx"


def _metrics_path(root: str | Path) -> Path:
    return _state_dir(root) / "metrics.json"


def _report_path(root: str | Path) -> Path:
    return _state_dir(root) / "pilot_report.json"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _safe_rate(numer: int | float, denom: int | float) -> float:
    denom_f = float(denom)
    if denom_f <= 0:
        return 0.0
    return float(numer) / denom_f


def _positive_count(count: int) -> int:
    value = int(count)
    if value <= 0:
        raise ValueError("count must be positive")
    return value


def _require_unresolved(metrics: "PilotMetrics", count: int, event: str) -> int:
    value = _positive_count(count)
    if metrics.unresolved_suggestions < value:
        raise ValueError(
            f"cannot record {event}: count={value} exceeds unresolved suggestions={metrics.unresolved_suggestions}"
        )
    return value


@dataclass
class PilotMetrics:
    """Raw causal counters for the Lux–Nyx pilot."""

    suggestion_total: int = 0
    suggestion_accepted: int = 0
    correction_total: int = 0
    archive_total: int = 0
    archive_promoted: int = 0
    promotion_total: int = 0
    baseline_metrics: dict[str, float] = field(default_factory=dict)
    baseline_source: str = ""
    baseline_observed_at: str = ""
    updated_at: str = ""

    @classmethod
    def load(cls, root: str | Path) -> "PilotMetrics":
        path = _metrics_path(root)
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return cls()
        if not isinstance(data, dict):
            return cls()

        # Tolerate older field names if any prior local report used them.
        if "correction_count" in data and "correction_total" not in data:
            data["correction_total"] = data.get("correction_count")
        if "baseline" in data and "baseline_metrics" not in data:
            baseline = data.get("baseline")
            if isinstance(baseline, dict):
                data["baseline_metrics"] = baseline

        allowed = {field.name for field in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        kwargs = {k: v for k, v in data.items() if k in allowed}
        try:
            return cls(**kwargs)
        except TypeError:
            return cls()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, root: str | Path) -> Path:
        self.updated_at = _now()
        path = _metrics_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    @property
    def resolved_suggestions(self) -> int:
        return max(0, int(self.suggestion_accepted) + int(self.correction_total))

    @property
    def unresolved_suggestions(self) -> int:
        return max(0, int(self.suggestion_total) - self.resolved_suggestions)

    def current_metric_values(self) -> dict[str, float]:
        return {
            "suggestion_acceptance_rate": _safe_rate(self.suggestion_accepted, self.suggestion_total),
            "correction_burden_per_suggestion": _safe_rate(self.correction_total, self.suggestion_total),
            "archive_to_promotion_conversion_quality": _safe_rate(self.archive_promoted, self.archive_total),
        }

    def invariant_errors(self) -> list[str]:
        errors: list[str] = []
        fields = {
            "suggestion_total": self.suggestion_total,
            "suggestion_accepted": self.suggestion_accepted,
            "correction_total": self.correction_total,
            "archive_total": self.archive_total,
            "archive_promoted": self.archive_promoted,
            "promotion_total": self.promotion_total,
        }
        for name, value in fields.items():
            if int(value) < 0:
                errors.append(f"{name} must be non-negative")
        if self.resolved_suggestions > int(self.suggestion_total):
            errors.append("resolved suggestions cannot exceed suggestion_total")
        if int(self.archive_promoted) > int(self.archive_total):
            errors.append("archive_promoted cannot exceed archive_total")
        return errors

    def sample_size_for(self, key: str) -> int:
        if key in {"suggestion_acceptance_rate", "correction_burden_per_suggestion"}:
            return int(self.suggestion_total)
        if key == "archive_to_promotion_conversion_quality":
            return int(self.archive_total)
        return 0


def _load_update_save(root: str | Path, updater) -> PilotMetrics:
    metrics = PilotMetrics.load(root)
    updater(metrics)
    metrics.save(root)
    write_pilot_report(root, metrics)
    return metrics


def record_suggestion(root: str | Path, action: str | None = None) -> PilotMetrics:
    """Record that a Lux–Nyx suggestion was surfaced.

    ``action`` is accepted for call-site traceability but not counted by type in
    this minimal pilot surface.
    """

    return _load_update_save(root, lambda m: setattr(m, "suggestion_total", int(m.suggestion_total) + 1))


def record_acceptance(root: str | Path, count: int = 1) -> PilotMetrics:
    def update(m: PilotMetrics) -> None:
        value = _require_unresolved(m, count, "acceptance")
        m.suggestion_accepted = int(m.suggestion_accepted) + value

    return _load_update_save(root, update)


def record_correction(root: str | Path, count: int = 1) -> PilotMetrics:
    def update(m: PilotMetrics) -> None:
        value = _require_unresolved(m, count, "correction")
        m.correction_total = int(m.correction_total) + value

    return _load_update_save(root, update)


def record_promotion(root: str | Path, count: int = 1) -> PilotMetrics:
    value = _positive_count(count)
    return _load_update_save(root, lambda m: setattr(m, "promotion_total", int(m.promotion_total) + value))


def record_archive_to_promotion(root: str | Path, count: int = 1) -> PilotMetrics:
    value = _positive_count(count)

    def update(m: PilotMetrics) -> None:
        m.archive_total = int(m.archive_total) + value
        m.archive_promoted = int(m.archive_promoted) + value
        m.promotion_total = int(m.promotion_total) + value

    return _load_update_save(root, update)


def set_baseline_metrics(
    root: str | Path,
    metrics: dict[str, float] | PilotMetrics,
    *,
    baseline_source: str = "",
    baseline_observed_at: str = "",
) -> PilotMetrics:
    """Freeze explicit baseline values without resetting live counters."""

    current = PilotMetrics.load(root)
    if isinstance(metrics, PilotMetrics):
        baseline_values = metrics.current_metric_values()
    else:
        baseline_values = {k: float(v) for k, v in metrics.items() if k in HEADLINE_METRIC_KEYS}
    current.baseline_metrics = baseline_values
    current.baseline_source = baseline_source
    current.baseline_observed_at = baseline_observed_at or _now()
    current.save(root)
    write_pilot_report(root, current)
    return current


def _comparison_direction(key: str, current: float, baseline: float | None) -> tuple[str, float | None]:
    if baseline is None:
        return "unconfigured", None
    delta = current - baseline
    if abs(delta) < 1e-12:
        return "same", 0.0
    higher_is_better = _HIGHER_IS_BETTER.get(key, True)
    better = delta > 0 if higher_is_better else delta < 0
    return ("better" if better else "worse"), delta


def _comparison_row(metrics: PilotMetrics, key: str) -> dict[str, Any]:
    current = metrics.current_metric_values().get(key, 0.0)
    baseline = metrics.baseline_metrics.get(key)
    if baseline is not None:
        baseline = float(baseline)
    direction, delta = _comparison_direction(key, current, baseline)
    sample_size = metrics.sample_size_for(key)
    return {
        "current": current,
        "baseline": baseline,
        "delta": delta,
        "direction": direction,
        "sample_size": sample_size,
        "sample_sufficient": sample_size >= MIN_PILOT_SAMPLE_SIZE,
        "sample_remaining": max(0, MIN_PILOT_SAMPLE_SIZE - sample_size),
    }


def pilot_promotion_verdict(report_or_metrics: dict[str, Any] | PilotMetrics) -> dict[str, Any]:
    if isinstance(report_or_metrics, PilotMetrics):
        report = build_pilot_report(report_or_metrics)
    else:
        report = report_or_metrics

    invariant_errors = report.get("invariant_errors", []) if isinstance(report, dict) else []
    if invariant_errors:
        verdict = "invalid-counters"
        reason = "Pilot counters violate measurement invariants."
    elif not bool(report.get("baseline_configured", False)):
        verdict = "baseline-unconfigured"
        reason = "No explicit baseline metrics have been frozen."
    else:
        health = report.get("measurement_health", {}) if isinstance(report, dict) else {}
        coverage = float(health.get("suggestion_resolution_coverage", 0.0) or 0.0)
        comparison = report.get("baseline_comparison", {}) if isinstance(report, dict) else {}
        rows = [comparison.get(k, {}) for k in HEADLINE_METRIC_KEYS if isinstance(comparison, dict)]
        if any(not bool(row.get("sample_sufficient", False)) for row in rows):
            verdict = "insufficient-samples"
            reason = "At least one headline metric has not reached the pilot sample gate."
        elif coverage < MIN_RESOLUTION_COVERAGE:
            verdict = "insufficient-resolution"
            reason = "Too many surfaced suggestions remain causally unresolved."
        elif any(row.get("direction") == "worse" for row in rows):
            verdict = "worse"
            reason = "At least one headline metric is worse than baseline."
        elif any(row.get("direction") == "better" for row in rows):
            verdict = "promote-candidate"
            reason = "All headline metrics are sampled, none are worse, and at least one is better."
        else:
            verdict = "no-lift"
            reason = "Headline metrics show no worse result but also no measured lift."

    return {
        "verdict": verdict,
        "reason": reason,
        "allowed_verdicts": list(PROMOTION_VERDICTS),
    }


def build_pilot_report(metrics: PilotMetrics | None = None, root: str | Path | None = None) -> dict[str, Any]:
    if metrics is None:
        if root is None:
            raise ValueError("build_pilot_report requires metrics or root")
        metrics = PilotMetrics.load(root)

    values = metrics.current_metric_values()
    baseline_configured = all(key in metrics.baseline_metrics for key in HEADLINE_METRIC_KEYS)
    comparison = {key: _comparison_row(metrics, key) for key in HEADLINE_METRIC_KEYS}
    report: dict[str, Any] = {
        "generated_at": _now(),
        "baseline_configured": baseline_configured,
        "baseline_source": metrics.baseline_source or None,
        "baseline_observed_at": metrics.baseline_observed_at or None,
        "counts": {
            "suggestion_total": int(metrics.suggestion_total),
            "suggestion_accepted": int(metrics.suggestion_accepted),
            "correction_total": int(metrics.correction_total),
            "archive_total": int(metrics.archive_total),
            "archive_promoted": int(metrics.archive_promoted),
            "promotion_total": int(metrics.promotion_total),
            "resolved_suggestions": metrics.resolved_suggestions,
            "unresolved_suggestions": metrics.unresolved_suggestions,
        },
        "metrics": values,
        "measurement_health": {
            "suggestion_resolution_coverage": _safe_rate(metrics.resolved_suggestions, metrics.suggestion_total),
            "min_resolution_coverage": MIN_RESOLUTION_COVERAGE,
        },
        "invariant_errors": metrics.invariant_errors(),
        "comparison_policy": {
            "min_pilot_sample_size": MIN_PILOT_SAMPLE_SIZE,
            "min_resolution_coverage": MIN_RESOLUTION_COVERAGE,
            "headline_metric_keys": list(HEADLINE_METRIC_KEYS),
            "metric_directionality": {
                key: ("higher_is_better" if higher else "lower_is_better")
                for key, higher in _HIGHER_IS_BETTER.items()
            },
        },
        "baseline_comparison": comparison,
    }
    report["promotion_verdict"] = pilot_promotion_verdict(report)
    return report


def write_pilot_report(root: str | Path, metrics: PilotMetrics | None = None) -> Path:
    metrics = metrics or PilotMetrics.load(root)
    report = build_pilot_report(metrics)
    path = _report_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
