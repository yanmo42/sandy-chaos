from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


_ALLOWED_VARIANT_IDS = (
    "single-scale-baseline",
    "multiframe-unconstrained-baseline",
    "neighbor-only-contract-model",
)


@dataclass(frozen=True)
class BenchmarkFrame:
    """One temporal frame input for the benchmark scaffold."""

    frame_id: str
    timestep: int
    observed_state: dict[str, float]
    latency: float = 0.0
    distortion: float = 0.0


@dataclass(frozen=True)
class BenchmarkCase:
    """Synthetic benchmark case used to inspect wiring before scoring exists."""

    case_id: str
    description: str
    frames: tuple[BenchmarkFrame, ...]
    target_state: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("case_id must be non-empty")
        if not self.description.strip():
            raise ValueError("description must be non-empty")
        if not self.frames:
            raise ValueError("benchmark case must include at least one frame")
        seen_ids: set[str] = set()
        previous_timestep: int | None = None
        for frame in self.frames:
            if not frame.frame_id.strip():
                raise ValueError("frame_id must be non-empty")
            if frame.frame_id in seen_ids:
                raise ValueError(f"duplicate frame_id {frame.frame_id!r}")
            seen_ids.add(frame.frame_id)
            if frame.latency < 0:
                raise ValueError("latency must be non-negative")
            if frame.distortion < 0:
                raise ValueError("distortion must be non-negative")
            # Strict causality: frames must be ordered by non-decreasing
            # timestep. Out-of-order frames would let a variant index a "future"
            # observation while pretending it was present/past.
            if previous_timestep is not None and frame.timestep < previous_timestep:
                raise ValueError(
                    "frames must be supplied in non-decreasing timestep order "
                    f"(frame {frame.frame_id!r} at t={frame.timestep} follows t={previous_timestep})"
                )
            previous_timestep = frame.timestep


@dataclass(frozen=True)
class VariantRunResult:
    """Inspectable output for a single variant.

    This scaffold intentionally reports no empirical score yet. The caller gets a
    clear reason instead of a fake metric.
    """

    variant_id: str
    status: str
    summary: str
    placeholder_metrics: dict[str, Any]
    causal_guards: tuple[str, ...]
    failure_modes: tuple[str, ...]


class BenchmarkVariant(Protocol):
    variant_id: str

    def describe(self) -> dict[str, Any]: ...

    def run(self, case: BenchmarkCase) -> VariantRunResult: ...


@dataclass(frozen=True)
class ScaffoldVariant:
    variant_id: str
    label: str
    interface_contract: tuple[str, ...]
    causal_guards: tuple[str, ...]
    failure_modes: tuple[str, ...]
    required_metadata_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.variant_id not in _ALLOWED_VARIANT_IDS:
            raise ValueError(f"unknown benchmark variant {self.variant_id!r}")

    def describe(self) -> dict[str, Any]:
        return {
            "variant_id": self.variant_id,
            "label": self.label,
            "interface_contract": list(self.interface_contract),
            "causal_guards": list(self.causal_guards),
            "failure_modes": list(self.failure_modes),
            "required_metadata_keys": list(self.required_metadata_keys),
            "status": "scaffold-only",
        }

    def _missing_metadata_keys(self, case: BenchmarkCase) -> tuple[str, ...]:
        return tuple(
            key for key in self.required_metadata_keys if key not in case.metadata
        )

    def run(self, case: BenchmarkCase) -> VariantRunResult:
        missing = self._missing_metadata_keys(case)
        if missing:
            # Falsification posture: the variant's declared contract precondition
            # is not satisfied, so the scaffold refuses to pretend it "ran" the
            # case. No empirical metrics are emitted, and the caller gets an
            # inspectable explanation instead of a silent pass.
            return VariantRunResult(
                variant_id=self.variant_id,
                status="scaffold-only-contract-unmet",
                summary=(
                    f"{self.label} refused benchmark case {case.case_id!r}: "
                    f"required metadata keys missing: {', '.join(missing)}."
                ),
                placeholder_metrics={
                    "prediction_error": None,
                    "contract_violation_rate": None,
                    "coherence_gain": None,
                    "latency_adjusted_utility": None,
                    "case_frame_count": len(case.frames),
                    "missing_metadata_keys": list(missing),
                },
                causal_guards=self.causal_guards,
                failure_modes=self.failure_modes,
            )
        return VariantRunResult(
            variant_id=self.variant_id,
            status="scaffold-only",
            summary=(
                f"{self.label} accepted benchmark case {case.case_id!r} but does not "
                "emit empirical scores yet."
            ),
            placeholder_metrics={
                "prediction_error": None,
                "contract_violation_rate": None,
                "coherence_gain": None,
                "latency_adjusted_utility": None,
                "case_frame_count": len(case.frames),
            },
            causal_guards=self.causal_guards,
            failure_modes=self.failure_modes,
        )


@dataclass(frozen=True)
class BenchmarkHarness:
    variants: tuple[ScaffoldVariant, ...]
    ablations: tuple[str, ...] = (
        "no-contract-projection",
        "no-shared-latent-space",
        "no-cross-frame-coupling",
        "all-to-all-coupling",
        "latency-distortion-removed",
    )

    def __post_init__(self) -> None:
        ids = tuple(variant.variant_id for variant in self.variants)
        if ids != _ALLOWED_VARIANT_IDS:
            raise ValueError(
                "benchmark harness must expose the canonical variant order: "
                + ", ".join(_ALLOWED_VARIANT_IDS)
            )

    def describe(self) -> dict[str, Any]:
        return {
            "variants": [variant.describe() for variant in self.variants],
            "ablations": list(self.ablations),
            "status": "scaffold-only",
            "notes": [
                "This harness is inspectable scaffolding only.",
                "No empirical results or promotion claims should be inferred from it.",
                "Strict causality is preserved by construction: variants only accept present/past-indexed frame inputs.",
            ],
        }

    def variant_interfaces(self) -> dict[str, list[str]]:
        """Expose inspectable per-variant interface contracts.

        This method is intentionally structural only. It does not execute variants
        or report benchmark scores.
        """

        return {
            variant.variant_id: list(variant.interface_contract)
            for variant in self.variants
        }

    def run_smoke_case(self) -> list[VariantRunResult]:
        case = make_smoke_case()
        return [variant.run(case) for variant in self.variants]



def make_default_harness() -> BenchmarkHarness:
    shared_guards = (
        "no future intervention terms in present-state inputs",
        "explicit latency accounting required for cross-frame transfer",
        "strictly inspectable placeholder outputs until scoring is implemented",
    )
    return BenchmarkHarness(
        variants=(
            ScaffoldVariant(
                variant_id="single-scale-baseline",
                label="Single-scale baseline",
                interface_contract=(
                    "accepts one benchmark case",
                    "ignores explicit multiframe coupling structure",
                    "returns scaffold-only placeholder metrics",
                ),
                causal_guards=shared_guards,
                failure_modes=(
                    "cannot represent frame-specific transfer assumptions",
                    "must not claim multiframe lift",
                ),
            ),
            ScaffoldVariant(
                variant_id="multiframe-unconstrained-baseline",
                label="Multiframe unconstrained baseline",
                interface_contract=(
                    "accepts one benchmark case",
                    "reads all declared frames without contract projection",
                    "returns scaffold-only placeholder metrics",
                ),
                causal_guards=shared_guards,
                failure_modes=(
                    "cannot expose contract residuals yet",
                    "must not imply neighbor-only admissibility",
                ),
            ),
            ScaffoldVariant(
                variant_id="neighbor-only-contract-model",
                label="Neighbor-only contract model",
                interface_contract=(
                    "accepts one benchmark case",
                    "expects neighbor-first frame topology metadata",
                    "returns scaffold-only placeholder metrics plus contract-facing placeholders",
                ),
                causal_guards=shared_guards,
                failure_modes=(
                    "contract residual function is not implemented yet",
                    "must not claim coherence lift before scored comparisons exist",
                    "refuses cases that omit neighbor_topology metadata",
                ),
                required_metadata_keys=("neighbor_topology",),
            ),
        )
    )



def make_smoke_case() -> BenchmarkCase:
    return BenchmarkCase(
        case_id="smoke-fast-meso-slow",
        description="Three-frame synthetic scaffold case for interface validation only.",
        frames=(
            BenchmarkFrame(
                frame_id="fast",
                timestep=0,
                observed_state={"signal": 1.0, "uncertainty": 0.2},
                latency=0.0,
                distortion=0.0,
            ),
            BenchmarkFrame(
                frame_id="meso",
                timestep=1,
                observed_state={"signal": 0.8, "uncertainty": 0.3},
                latency=0.1,
                distortion=0.05,
            ),
            BenchmarkFrame(
                frame_id="slow",
                timestep=2,
                observed_state={"signal": 0.6, "uncertainty": 0.4},
                latency=0.2,
                distortion=0.08,
            ),
        ),
        target_state={"signal": 0.75},
        metadata={
            "purpose": "smoke-test",
            "causal_scope": "present-and-past-observations-only",
            "neighbor_topology": (
                ("fast", "meso"),
                ("meso", "slow"),
            ),
        },
    )
