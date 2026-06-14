# Contract 4 Receipt: Moving-Observer Anticipatory ΔI (AUD-004)

- **Date**: Sunday, June 14, 2026
- **Branch**: `contracts/contract-4-moving-observer`
- **Verdict**: ADVANCE

## Quantitative Results

- **Best $\Delta I$ Observed**: $0.1714$ bits (observed at $Fr = 0.3$, $\tau = 1.0$)
- **AR Forecaster Beaten**: YES
  - At $Fr = 0.3, \tau = 1.0$: $\Delta I = 0.1714$ bits, while the strictly past AR(p) forecaster achieved only $0.0204$ bits.
  - At $Fr = 0.5, \tau = 1.0$: $\Delta I = 0.1700$ bits, while the strictly past AR(p) forecaster achieved only $0.0205$ bits.
  - At $Fr = 0.7, \tau = 1.0$: $\Delta I = 0.1688$ bits, while the strictly past AR(p) forecaster achieved only $0.0038$ bits.
  - At $Fr = 0.9, \tau = 5.0$: $\Delta I = 0.0276$ bits, while the strictly past AR(p) forecaster achieved only $0.0031$ bits.

## Pre-Registered Failure Condition

- **Condition**: if $\Delta I \le 0$ across all $Fr < 1$, OR AR forecaster matches channel-present $\Delta I$, future-like advantage fails at L2 and must be relabeled.
- **Triggered**: NO
  - $\Delta I$ is strictly positive for all subcritical Froude numbers $Fr \in \{0.3, 0.5, 0.7, 0.9\}$.
  - The moving observer's information gain $\Delta I$ significantly outperforms the strictly past-history AR forecaster across multiple configurations, particularly at short lead times and very long lead times where the local historical correlation decays.

## T-002 Matrix Status

- **Status**: Updated to include `T-002a` sub-row as `PASS` in `docs/theory-implementation-matrix.md`.
- **Evidence Payload**: Verified successfully with `scripts/validate_foundations.py --payload-file memory/research/moving_observer_results_20260614.json`.
