"""Benchmark scaffolds for theory-facing validation surfaces."""

from .temporal_predictive_processing import (
    BenchmarkCase,
    BenchmarkFrame,
    BenchmarkHarness,
    BenchmarkVariant,
    ScaffoldVariant,
    VariantRunResult,
    make_default_harness,
    make_smoke_case,
)

__all__ = [
    "BenchmarkCase",
    "BenchmarkFrame",
    "BenchmarkHarness",
    "BenchmarkVariant",
    "ScaffoldVariant",
    "VariantRunResult",
    "make_default_harness",
    "make_smoke_case",
]
