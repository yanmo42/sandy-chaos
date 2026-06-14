# Sandy Chaos — Contract 2 Receipt

This receipt documents the successful completion of **Contract 2: Kerr Validation Rebuild (AUD-001)**.

## Execution Metadata

- **Date:** Sunday, June 14th, 2026
- **Reference UTC:** 2026-06-14 09:51 UTC
- **Branch:** `contracts/contract-2-kerr-rebuild`
- **Results File:** `memory/research/kerr_v2_results_20260614.json`
- **Plot Image:** `memory/research/kerr_v2_asymmetry_plot.png`
- **Evidence Payload:** `memory/research/kerr_asymmetry_2026-03/t015_rebuild_evidence.json`

## Contract 2 Deliverables and Outcomes

### 1. T-015 Final Decision
- **Final Decision:** PASS
- **Confidence:** High
- **Description:** Rebuilt using equatorial timelike geodesics (Hamiltonian $H = -0.5$) and numerical proper-time integration.

### 2. Sagnac Distinguishable from Kerr
- **Sagnac Distinguishable:** YES
- **Description:** By selecting $\omega = a / r_{\text{orbit}}^3$ and $v = 1/\sqrt{r_{\text{orbit}}}$, Sagnac-flat matches the Kerr coordinate-time asymmetry exactly. However, the proper-time asymmetry curves of Kerr and Sagnac remain highly distinguishable due to general relativistic gravitational time dilation and frame dragging in Kerr. Kerr proper-time asymmetry scales up to 8.15% at $a/M = 0.9$ compared to Sagnac-flat's 5.69%.

### 3. Error Bar Range
- **Kerr Error Bar:** $1.0 \times 10^{-11}$ to $5.9 \times 10^{-11}$
- **Sagnac Error Bar:** $2.9 \times 10^{-15}$ to $6.7 \times 10^{-13}$
- **Description:** Maximum absolute discrepancy across step sizes $h \in [0.01, 0.05, 0.1]$. The tiny error bars confirm that numerical integration is extremely precise, stable, and the measured asymmetry difference is a genuine physical phenomenon, not an integration artifact.

### 4. Implication for Contract 6
- **Contract 6 Path:** WIRE
- **Description:** Since Kerr's curvature-induced proper-time asymmetry is confirmed as distinguishable from Langevin-Minkowski Sagnac-flat, we proceed with the WIRE branch of Contract 6. This involves deriving a physical `backward_attenuation` profile from the Kerr geometry and integrating it directly into `VortexChannel`, replacing the current hand-set scalar.

## Verification Logs

- `scripts/validate_foundations.py` passes successfully with the new payload.
- All 346 unit tests in the repository pass.
