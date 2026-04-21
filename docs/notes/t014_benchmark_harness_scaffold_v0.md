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
- per-variant metadata invariants for declared structure: the `neighbor-only-contract-model` refuses cases whose `neighbor_topology` is empty, references unknown `frame_id`s, or declares a neighbor edge running backward in time (the declared topology must respect strict forward causality just like the frame ordering itself)
- pinned canonical ablation list on `BenchmarkHarness.ablations`: silent reorder, rename, or addition would desync the ablation-table contract from the spec note and now fails loudly
- pinned per-variant required-metadata mapping: baselines must stay minimal-contract (no required metadata), and `neighbor-only-contract-model` must keep `neighbor_topology` as its declared precondition; silent drift either way now fails loudly
- constructor-level ablation-id validation on `BenchmarkHarness`: any direct construction whose `ablations` tuple drifts from the canonical list (unknown id, duplicate id, missing canonical id, or reordered) fails at `__post_init__` with a named detail, so silent typo/rename can no longer slip past as a valid scaffold harness
- pinned smoke-result emission order on `run_smoke_case()`: results must pair positionally with `harness.variants` in the canonical variant order, so a shuffled emission cannot silently mislabel an interface contract against the wrong `variant_id`

Not included yet:

- dataset generator beyond the smoke fixture
- contract residual implementation
- scored baseline comparison
- promotion evidence for matrix row T-014

Interpretation rule:

This scaffold is for inspection, wiring, and testability only. It must not be cited as empirical support for T-014, and it does not change the row's current `REVIEW` posture. The smoke validation checks for scaffold-only status plus non-empty causal guards and failure modes so that missing falsification hooks fail loudly.
