# NFEM benchmark harness scaffold

This directory includes an inspectable benchmark harness skeleton for temporal predictive processing.

## Current status

- Scaffold only, no empirical benchmark scores are emitted.
- Three exposed variant interfaces:
  - `single-scale-baseline`
  - `multiframe-unconstrained-baseline`
  - `neighbor-only-contract-model`
- Strict causality guard: interfaces consume only present and past-indexed frame inputs.
- Falsification-oriented framing: each variant declares explicit failure modes and causal guardrails.
- Contract preconditions are enforced at run time: the `neighbor-only-contract-model` variant refuses cases missing its required `neighbor_topology` metadata, returning `status="scaffold-only-contract-unmet"` instead of a silent pass.

Use `make_default_harness()` and inspect `harness.describe()` or `harness.variant_interfaces()` to verify wiring before any scoring implementation exists.
