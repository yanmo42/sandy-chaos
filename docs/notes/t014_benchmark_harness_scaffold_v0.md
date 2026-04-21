# T-014 Benchmark Harness Scaffold v0

Status: inspectable scaffold only.

This note records the first code surface for the T-014 temporal predictive-processing benchmark harness under `nfem_suite/benchmarks/temporal_predictive_processing.py`.

Included now:

- canonical variant interfaces for:
  - `single-scale-baseline`
  - `multiframe-unconstrained-baseline`
  - `neighbor-only-contract-model`
- one synthetic smoke case covering `fast`, `meso`, and `slow` frames, with neighbor-topology metadata wired in for the contract variant
- explicit placeholder outputs that refuse to report empirical benchmark scores
- causal guard text stating that present-state inputs must not depend on future interventions
- failure-mode declarations per variant so falsification pressure is inspectable before any scoring exists
- per-variant contract preconditions enforced at `run()` time: the `neighbor-only-contract-model` declares `required_metadata_keys=("neighbor_topology",)` and returns `status="scaffold-only-contract-unmet"` with the missing keys listed when a case omits them, rather than silently passing

Not included yet:

- dataset generator beyond the smoke fixture
- contract residual implementation
- scored baseline comparison
- promotion evidence for matrix row T-014

Interpretation rule:

This scaffold is for inspection, wiring, and testability only. It must not be cited as empirical support for T-014, and it does not change the row's current `REVIEW` posture. The smoke validation checks for scaffold-only status plus non-empty causal guards and failure modes so that missing falsification hooks fail loudly.
