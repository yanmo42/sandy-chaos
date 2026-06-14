# Contract 3 Verification Note: Hyperbolic Subcritical Solver

- **Date**: Sunday, June 14, 2026
- **Verifier**: google/gemini-3.5-flash (Personal Assistant)
- **Verdict**: APPROVED

## Physics Verification Analysis & Checklist

All physics checklist items have been carefully analyzed and successfully verified:

1. **Hyperbolic Nature of the PDE**: The 1D linearized shallow-water PDE is correctly modeled as a hyperbolic system by transforming the coupled equations into decoupled Riemann invariants:
   $$\frac{\partial w_1}{\partial t} + \lambda_1 \frac{\partial w_1}{\partial x} = 0 \quad (\lambda_1 = u + c_0 > 0)$$
   $$\frac{\partial w_2}{\partial t} + \lambda_2 \frac{\partial w_2}{\partial x} = 0 \quad (\lambda_2 = u - c_0 < 0)$$
   These are solved using a first-order upwind scheme with no artificial or physical diffusion. Thus, the system exhibits a strictly finite wave propagation speed, unlike parabolic implementations which would be physical non-sensical for this wave-dominated system.

2. **Upstream Wave Speed implementation ($c_{up}$)**: The upstream characteristic wave propagation speed is correctly formulated as $c_{up} = \sqrt{gH} - u$. For $Fr < 1$ (subcritical flow), the flow velocity $u = Fr \sqrt{gH} < \sqrt{gH}$, meaning $c_{up} > 0$. This ensures waves propagate upstream against the flow at a positive, finite speed.

3. **Measured vs. Theoretical Delay ($\tau_{measured} \approx \tau_{theoretical}$)**:
   - Theoretical delay: $\tau_{theoretical} = \frac{L - x_{obs}}{c_{up}} = 3.1928 \text{ s}$
   - Measured delay (wavefront midpoint threshold = 0.5): $\tau_{measured} = 3.1938 \text{ s}$
   - Discrepancy (midpoint threshold): **0.03%** (well within the required 10% limit)
   - Measured delay (10% threshold): $\tau_{measured} = 3.0347 \text{ s}$
   - Discrepancy (10% threshold): **4.95%** (well within the required 10% limit)

4. **Parabolic Baseline (Leakage) Comparison**: The Crank-Nicolson pure-diffusion baseline was evaluated under the exact same grid configurations. In contrast to the hyperbolic system, the parabolic system propagates information with infinite speed, exhibiting instantaneous "leakage":
   - Threshold $10^{-6}$ onset: 0.6710 s
   - Threshold $10^{-4}$ onset: 1.0601 s
   - Threshold $10^{-2}$ onset: 2.4217 s
   The onset delay continuously approaches zero as the detection threshold is reduced, verifying the infinite propagation speed property of the parabolic baseline.

5. **Pre-Registration Predictions**: The required five mathematical/physical pre-registration predictions are written explicitly at the very top of `research/subcritical_hyperbolic_demo.py` prior to the main code structure, adhering strictly to scientific rigor.

6. **MI vs. Froude Regime Transition**: The Froude sweep sweep shows physically consistent behavior:
   - For $Fr \in [0.05, 0.20]$, $I(Q; B) \approx 1.0000$ bits (full wave transmission).
   - For $Fr = 0.30$, $I(Q; B) \approx 0.7819$ bits (wave is arriving).
   - For $Fr = 0.35$, $I(Q; B) \approx 0.0007$ bits (wave has not yet arrived).
   - For $Fr \ge 0.40$, $I(Q; B) = 0.0000$ bits (upstream wave has been swept downstream or moves too slowly to arrive in the observation window).
   As $Fr \to 1$, $c_{up} \to 0$, causing wave travel time to approach infinity, suppressing any mutual information transmission within the finite $t_{meas} = 4.5$ s window.

## Conclusion

This implementation meets all physical, mathematical, and structural requirements of Contract 3 (AUD-003 / T-002). The verification is complete and approved.
