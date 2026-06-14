# Contract 3 Receipt: Hyperbolic Subcritical Mechanism (AUD-003)

- **Date**: Sunday, June 14, 2026
- **Branch**: `contracts/contract-3-hyperbolic`
- **Kill Criterion Met**: YES

## Delay Measurement Result

- **Theoretical Onset Delay ($t_{theoretical}$)**: 3.1928 seconds
- **Measured Onset Delay ($t_{measured}$)**: 3.1938 seconds (measured at wavefront midpoint threshold = 0.5)
- **Measured Onset Delay (10% threshold)**: 3.0347 seconds
- **Discrepancy (midpoint threshold)**: 0.03% (well within the required 10% limit)
- **Discrepancy (10% threshold)**: 4.95% (well within the required 10% limit)

## Mutual Information Regime Result

- **Transition Profile (measured at $t_{meas} = 4.5$ seconds with noise standard deviation $\sigma = 0.05$):**
  - **$Fr = 0.05$ (highly subcritical)**: $I(Q; B) = 1.0000$ bits (wave has arrived, full legibility)
  - **$Fr = 0.20$ (base subcritical)**: $I(Q; B) = 1.0000$ bits (wave has arrived, full legibility)
  - **$Fr = 0.30$ (moderate subcritical)**: $I(Q; B) = 0.7819$ bits (wave is arriving, partial legibility)
  - **$Fr = 0.35$ (near critical)**: $I(Q; B) = 0.0007$ bits (wave has not yet arrived due to slow propagation speed $c_{up}$)
  - **$Fr \ge 0.40$ (critical / supercritical boundary)**: $I(Q; B) = 0.0000$ bits (no information has arrived within the finite observation window)

This sweep demonstrates a clear, physically consistent, Froude-limited regime transition in mutual information.

## Comparator Result

The pure-diffusion parabolic baseline was evaluated using Crank-Nicolson on the exact same grid:
- **Parabolic onset at threshold $10^{-6}$**: 0.6710 seconds
- **Parabolic onset at threshold $10^{-4}$**: 1.0601 seconds
- **Parabolic onset at threshold $10^{-2}$**: 2.4217 seconds

As predicted, the parabolic system exhibits instantaneous leakage: reducing the detection threshold shifts the measured onset delay closer to zero, whereas the hyperbolic system has a strictly bounded and robust onset delay that reflects the finite upstream wave propagation speed.

## T-002 Matrix Status

- **Status**: Updated from `REVIEW` to `PASS` in `docs/theory-implementation-matrix.md`.
- **Evidence Payload**: Verified successfully with `scripts/validate_foundations.py --payload-file memory/research/t002_hyperbolic_evidence.json`.
