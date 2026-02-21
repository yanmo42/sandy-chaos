# Math Appendix

This appendix collects compact formal elements used across the core docs.  
Derivations are intentionally lightweight; this project prioritizes conceptual clarity plus falsifiable structure.

---

## A) Forward dynamics and retrodiction

Forward evolution:

\[
x_{t+\Delta} = F_\Delta(x_t, a_t, \eta_t)
\]

Retrodictive map:

\[
\hat{a}_t = R(x_{t+\Delta})
\]

High-fidelity retrodiction condition:

\[
P(\hat{a}_t = a_t) \approx 1
\]

Anticipatory policy under expected future evaluation:

\[
a_t^* = \arg\max_a\;\mathbb{E}\big[U(a,\Psi(R(F_\Delta(x_t,a,\eta_t))))\mid \mathcal{I}_t\big]
\]

Causality safety criterion:

\[
P(a_t\mid do(x_{t+\Delta}=z),\mathcal{I}_t)=P(a_t\mid\mathcal{I}_t)
\]

---

## B) Tempo Tracer channel formalization

Channel map in curved medium:

\[
Y = \mathcal{F}_{\text{Kerr}}(X,u,n)
\]

Null-geodesic Hamiltonian constraint:

\[
H = \tfrac{1}{2}g^{\mu\nu}p_\mu p_\nu \approx 0
\]

Temporal alignment metric:

\[
E_{align}=\left|(\tau_{recv}-\tau_{send})-\tau_{expected}\right|
\]

Packet schema:

\[
P = \{payload,\tau_{send},\sigma_{send},confidence,checksum,validity\_window\}
\]

---

## C) Micro-observer coupling

Observation map:

\[
O_t = \mathcal{M}(L_t,S_t,\epsilon_t)
\]

State transition map:

\[
L_{t+1}=\mathcal{T}(L_t,A_t,\eta_t)
\]

Read-write effect abstraction:

\[
\Delta L_t \propto \Phi(S_t,\text{measurement policy},\text{feedback loop})
\]

Consciousness proxy index:

\[
\chi = f(B,D,C,R)
\]

---

## D) Neuro-roadmap latent decoding abstraction

\[
\hat{z}_{idea}(t)=f_\theta\big(X_{neural}(t-\Delta:t),C_{task},C_{history}\big)
\]

Where:

- \(X_{neural}\): measured neural signals,
- \(C_{task}\): current task context,
- \(C_{history}\): temporal prior/history context,
- \(\hat{z}_{idea}\): inferred semantic-affective latent representation.

---

## E) Validation metric set (minimal)

- ROC/AUC (detection)
- KL divergence (distribution shift)
- Mutual information lower bounds \(I(U;Y)\)
- Alignment error \(E_{align}\)
- Calibration metrics (Brier score, reliability curves)

Claims should be accepted only with reproducible significance and clearly stated failure thresholds.