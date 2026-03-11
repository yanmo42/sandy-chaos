# Math Appendix

> **Axiomatic grounding.** Equations in this appendix are intended to be
> traceable to the formal foundations in
> [`math_foundations_zf.md`](math_foundations_zf.md), together with explicitly
> stated modeling assumptions where needed.
> Section references (§0–§14) point to derivation layers in that document.
> Working chain: $\varnothing \to \mathbb{N} \to \mathbb{Z} \to \mathbb{Q} \to \mathbb{R} \to \mathbb{C} \to (M, g_{\mu\nu}) \to \text{Kerr} \to \text{Sandy Chaos}$. 

This appendix collects compact formal elements used across the core docs.  
Derivations are intentionally lightweight; this project prioritizes conceptual clarity plus falsifiable structure.

---

## A) Forward dynamics, retrodiction, and boundary propagation

Forward evolution:

$$
x_{t+\Delta} = F_\Delta(x_t, a_t, \eta_t)
$$

Retrodictive map:

$$
\hat{a}_t = R(x_{t+\Delta})
$$

High-fidelity retrodiction condition:

$$
P(\hat{a}_t = a_t) \approx 1
$$

Boundary-propagation field (downstream-conditioned):

$$
\partial_t q + u\,\partial_x q = D\,\partial_{xx} q + \eta,
\qquad q(L,t)=B(t)
$$

Subcritical upstream-legibility condition:

$$
Fr=\frac{u}{\sqrt{gh}}<1
$$

Local structural update:

$$
s_{t+\Delta}=\Pi\big(s_t,\nabla q(x_s,t),\zeta_t\big)
$$

Causality safety criterion:

$$
P(s_t\mid do(B_{t+\Delta}=b),\mathcal{I}_t)=P(s_t\mid\mathcal{I}_t)
$$

---

## B) Tempo Tracer channel formalization

Channel map in curved medium:

$$
Y = \mathcal{F}_{\text{Kerr}}(X,u,n)
$$

Null-geodesic Hamiltonian constraint:

$$
H = \tfrac{1}{2}g^{\mu\nu}p_\mu p_\nu \approx 0
$$

Temporal alignment metric:

$$
E_{align}=\left|(\tau_{recv}-\tau_{send})-\tau_{expected}\right|
$$

Packet schema (current minimal):

$$
P_{min} = \{payload,\tau_{send},\sigma_{send},confidence,checksum\}
$$

Planned experiment-layer extensions may add fields such as `validity_window`, `boundary_tag`, `narrative_context`, or `audit_trace`, but those are not part of the baseline protocol contract.

---

## C) Micro-observer coupling

Observation map:

$$
O_t = \mathcal{M}(L_t,S_t,\epsilon_t)
$$

State transition map:

$$
L_{t+1}=\mathcal{T}(L_t,A_t,\eta_t)
$$

Read-write effect abstraction:

$$
\Delta L_t \propto \Phi(S_t,\text{measurement policy},\text{feedback loop})
$$

Consciousness proxy index:

$$
\chi = f(B,D,C,R)
$$

---

## D) Neuro-roadmap latent decoding abstraction

$$
\hat{z}_{idea}(t)=f_\theta\big(X_{neural}(t-\Delta:t),C_{task},C_{history}\big)
$$

Where:

- $X_{neural}$: measured neural signals,
- $C_{task}$: current task context,
- $C_{history}$: temporal prior/history context,
- $\hat{z}_{idea}$: inferred semantic-affective latent representation.

---

## E) Validation metric set (minimal)

- ROC/AUC (detection)
- KL divergence (distribution shift)
- Mutual information lower bounds $I(U;Y)$
- Alignment error $E_{align}$
- Calibration metrics (Brier score, reliability curves)

Claims should be accepted only with reproducible significance and clearly stated failure thresholds.