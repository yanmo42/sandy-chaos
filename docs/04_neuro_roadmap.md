# 04 Neuro Roadmap

## 1) Purpose

This roadmap translates the framework into a staged research and implementation program.

Principle: **evidence core first, moonshot second**.

---

## 2) Defensible scope (near-term)

Current state of the field supports partial decoding and alignment in constrained settings:

- motor intent,
- limited speech/imagery classes,
- coarse affective trends,
- timing-aware prediction under uncertainty.

It does not support full “mind readout.”

---

## 3) Architecture stance

Use a multi-timescale framing:

- fast loops (rapid selection and correction),
- meso loops (routing and contextual alignment),
- slow loops (goal continuity and identity-level constraints).

Neuromorphic/event-driven intuitions are useful, but should remain tied to measurable benchmarks.

---

## 4) Measurement and modeling strategy

Practical pipeline:

1. Multimodal acquisition (e.g., EEG + context/behavioral traces).
2. Signal conditioning and drift control.
3. Latent representation learning (semantic + affective factors).
4. Uncertainty-aware decoding and abstention logic.
5. Human-in-the-loop correction and calibration updates.

Minimal representation equation:

\[
\hat{z}_{idea}(t)=f_\theta\big(X_{neural}(t-\Delta:t), C_{task}, C_{history}\big)
\]

---

## 5) Phased program

### Phase A — Constrained decode foundations

- standardized tasks (imagery, inner speech, affect labels),
- repeated-session reliability,
- baseline calibration metrics.

### Phase B — Temporal fusion

- combine modalities and context priors,
- quantify gains over single-modality baselines,
- stress-test non-stationarity.

### Phase C — Semantics-first externalization

- decode to structured latent semantics before rendering,
- keep confidence intervals explicit,
- require abstention under uncertainty.

### Phase D — Utility and governance

- evaluate communication/assistive value,
- monitor autonomy drift,
- enforce privacy and audit requirements.

---

## 6) Safety invariants

1. Consent with revocation at any time
2. Data minimization + scoped usage
3. Auditability of inference pathways
4. Right to abstain (no forced inference output)
5. No covert coercive optimization

---

## 7) Moonshot (clearly labeled speculative)

Long-term target:

> user-authored internal content can be externalized with enough fidelity to improve human-to-human meaning transfer beyond language alone.

This remains speculative and must not be conflated with near-term evidence claims.

---

## 8) Failure conditions

- performance collapses outside narrow lab settings,
- confidence is badly miscalibrated,
- personalization induces unstable dependence,
- no reproducible gain over simpler baselines.

If these occur, the roadmap must be revised before escalation.

---

## 9) Relationship to other docs

- **[01 Foundations](01_foundations.md)**: claim boundaries and causality discipline.
- **[02 Tempo Tracer Protocol](02_tempo_tracer_protocol.md)**: transport/timing/testing mechanics.
- **[03 Micro-Observer & Agency](03_micro_observer_agency.md)**: agency model and ethics constraints.