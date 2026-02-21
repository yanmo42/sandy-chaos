# 02 Tempo Tracer Protocol

## 1) Purpose

This document defines the operational layer of Tempo Tracer: how signaling, timing, and validation work under strict causality constraints.

The objective is **forecasting advantage without retrocausality**.

---

## 2) Channel model (minimal formal core)

We model propagation through a curved-spacetime medium as:

$$
Y = \mathcal{F}_{\text{Kerr}}(X, u, n)
$$

- $X$: initial photon/observable ensemble
- $u$: controlled modulation schedule
- $n$: background noise
- $Y$: received observables

Null-geodesic consistency condition:

$$
H = \tfrac{1}{2}g^{\mu\nu}p_\mu p_\nu \approx 0
$$

If this fails numerically, the run is invalid.

---

## 3) Communication modes

### Mode A — Direct Light Path

- Baseline line-of-sight signaling
- Light-speed limited
- Usually highest fidelity / easiest attribution

### Mode B — Shared Medium (Vortex / BH-mediated)

- Both parties encode and decode through a shared geometric channel
- Latency and quality can be asymmetric (A→B differs from B→A)
- Most relevant for "future-like" timing asymmetry effects

### Mode C — Archival / Beacon

- Long-lived structured signatures in outside-horizon observables
- Intended for delayed recovery and decoding

---

## 4) Timing planes and packet semantics

We separate three timing layers:

- External reference time: $t$
- Observer-local clocks: $\tau_A, \tau_B$
- Protocol/meta-time: $\sigma$

Canonical packet schema:

$$
P = \{\text{payload},\; \tau_{\text{send}},\; \sigma_{\text{send}},\; \text{confidence},\; \text{checksum},\; \texttt{validity\_window}\}
$$


Interpretation requires all three planes: data, timing, trust.

---

## 5) Causality-safe interpretation rule

Tempo Tracer allows:

- forward physical transport,
- observer-dependent timing asymmetry,
- anticipatory behavior based on expected future inference.

Tempo Tracer forbids:

- ontic backward causation,
- superluminal operational claims,
- in-horizon message recovery claims.

"Future-like" effects must be reducible to forward dynamics + timing asymmetry + inference.

---

## 6) Falsification-first metrics

Minimum validation stack:

1. **Detection performance**: ROC/AUC for controlled modulation vs baseline
2. **Distributional shift**: KL divergence between natural and modulated observables
3. **Information transfer**: lower bound on $I(U;Y)$
4. **Temporal consistency**:

$$
E_{align}=\left|(\tau_{recv}-\tau_{send})-\tau_{expected}\right|
$$

5. **Forecast reliability**: calibration curves, Brier score, false alarm rate

If reproducibility/significance thresholds fail, the claim fails.

---

## 7) Protocol workflow (practical)

1. Define claim tier (defensible / plausible / speculative).
2. Specify encoding schedule $u$ and baseline conditions.
3. Run geodesic quality checks and reject invalid trajectories.
4. Decode with uncertainty-aware inference.
5. Audit timing alignment, trust metadata, and reproducibility.

---

## 8) Relationship to other docs

- **[01 Foundations](01_foundations.md)** explains the causal boundary and epistemic retro-influence distinction.
- **[03 Micro-Observer & Agency](03_micro_observer_agency.md)** covers observer-state coupling and ethics.
- **[Math Appendix](math_appendix.md)** contains extended equation references.