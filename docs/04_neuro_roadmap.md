# 04 Neuro Roadmap

> **Status:** canonical roadmap for the neural evidence / decoding lane.
>
> This document no longer tries to carry every multiscale cognition question in Sandy Chaos. Its narrower job is to define the **neural measurement and decoding lane**: what can be defensibly measured, inferred, and externalized from neural signals under bounded conditions.
>
> Related docs:
>
> - `docs/03_micro_observer_agency.md`
> - `docs/05_hyperstition_temporal_bridge_analysis.md`
> - `docs/13_nested_temporal_domains.md`
> - `docs/14_cognitive_tempo_orchestration.md`
>
> Claim posture:
>
> - **Defensible now:** constrained neural decoding and timing-aware inference are possible in narrow settings.
> - **Plausible but unproven:** multiscale coupling models may improve decode quality and calibration.
> - **Speculative:** high-fidelity internal-content externalization could someday exceed language-only communication.

## 1) Purpose

This roadmap translates the Sandy Chaos framework into a staged **neural evidence** program.

Principle: **evidence core first, moonshot second**.

This is only one lane of the broader architecture.

The current canonical split is:

1. **Neuro Roadmap (`04`)**
   - neural measurement, decoding, uncertainty, externalization.
2. **Nested Temporal Domains (`13`)**
   - multiscale coupling grammar across fast / meso / slow domains.
3. **Cognitive Tempo Orchestration (`14`)**
   - practical external scaffolding and interface timing for improved action readiness.

That separation matters because the repo's strongest near-term progress is not identical to strong neural readout.

---

## 2) Defensible scope (near-term)

Current state of the field supports partial decoding and alignment in constrained settings:

- motor intent,
- limited speech/imagery classes,
- coarse affective trends,
- timing-aware prediction under uncertainty.

It does **not** support full “mind readout,” unrestricted access to subjective experience, or a solved mapping from neural signals to private qualitative state.

---

## 3) Architecture stance

Use a multi-timescale framing, but keep the role of this document explicit.

Relevant bands include:

- fast loops (rapid selection and correction),
- meso loops (routing and contextual alignment),
- slow loops (goal continuity and identity-level constraints).

A useful discipline rule is to treat these as **nested temporal domains** with neighbor-first coupling:

- fast ↔ meso,
- meso ↔ slow,
- and cross-band exchange should use bounded summaries, gains, or errors rather than assumed full-state access.

For continuity with Yggdrasil (`docs/12_yggdrasil_continuity_architecture.md` §5 Rule 5), these bands map onto the project's cadence surfaces as **fast = edge**, **meso = bridge**, **slow = spine**. The mapping stays strictly forward-causal: edge outputs can inform bridge summaries, and bridge summaries can justify spine revisions, but neuro-lane fast-loop activity should not directly rewrite slow-band policy.

But this document does **not** define the full coupling grammar. That job belongs to **[13 Nested Temporal Domains](13_nested_temporal_domains.md)**.

Likewise, this document does **not** define the external scaffolding / intervention lane. That job belongs to **[14 Cognitive Tempo Orchestration](14_cognitive_tempo_orchestration.md)**.

Neuromorphic/event-driven intuitions remain useful, but should stay tied to measurable benchmarks rather than doing explanatory work by themselves.

---

## 4) Measurement and modeling strategy

Practical pipeline:

1. Multimodal acquisition (for example EEG plus task/context/behavioral traces).
2. Signal conditioning and drift control.
3. Latent representation learning (semantic + affective factors).
4. Uncertainty-aware decoding and abstention logic.
5. Human-in-the-loop correction and calibration updates.

Minimal representation equation:

$$
\hat{z}_{idea}(t)=f_\theta\big(X_{neural}(t-\Delta:t), C_{task}, C_{history}\big)
$$

where:

- $X_{neural}$ is observed neural data,
- $C_{task}$ is task context,
- $C_{history}$ is longer-horizon prior information,
- and $\hat{z}_{idea}$ is a bounded latent estimate rather than a claim of full internal-state recovery.

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

- evaluate communication / assistive value,
- monitor autonomy drift,
- enforce privacy and audit requirements.

---

## 6) Relationship to the broader roadmap

The neural lane should now be read as one component of a broader system, not as the master roadmap for all cognition work.

### 6.1 What belongs here

- neural sensing tradeoffs,
- decode calibration,
- semantics-first externalization,
- abstention logic,
- privacy and consent constraints.

### 6.2 What belongs mostly in `13`

- admissible cross-band coupling rules,
- neighbor-layer transfer constraints,
- latency / distortion / reconstruction burden,
- multiscale architecture independent of literal neural sensing.

### 6.3 What belongs mostly in `14`

- prompt timing,
- pacing and salience scaffolding,
- task-chunking orchestration,
- bounded external interventions,
- execution support without action-forcing.

This separation keeps Sandy Chaos from using “neuro” as an umbrella term for work that is actually architectural or interface-oriented.

---

## 7) Safety invariants

1. Consent with revocation at any time
2. Data minimization + scoped usage
3. Auditability of inference pathways
4. Right to abstain (no forced inference output)
5. No covert coercive optimization

These remain non-negotiable. If they cannot be preserved, the neural lane should not be escalated.

---

## 8) Moonshot (clearly labeled speculative)

Long-term target:

> user-authored internal content can be externalized with enough fidelity to improve human-to-human meaning transfer beyond language alone.

This remains speculative and must not be conflated with near-term evidence claims.

Any stronger claim must still pass through:

- constrained benchmarks,
- uncertainty calibration,
- privacy and consent gates,
- and comparison against simpler non-neural alternatives.

---

## 9) Failure conditions

- performance collapses outside narrow lab settings,
- confidence is badly miscalibrated,
- personalization induces unstable dependence,
- no reproducible gain over simpler baselines,
- or the document starts smuggling architectural or orchestration claims under the label of neural evidence.

If these occur, the roadmap must be revised before escalation.

---

## 10) Relationship to other docs

- **[01 Foundations](01_foundations.md)**: claim boundaries and causality discipline.
- **[02 Tempo Tracer Protocol](02_tempo_tracer_protocol.md)**: transport/timing/testing mechanics.
- **[03 Micro-Observer & Agency](03_micro_observer_agency.md)**: agency model and ethics constraints.
- **[13 Nested Temporal Domains](13_nested_temporal_domains.md)**: multiscale coupling grammar.
- **[14 Cognitive Tempo Orchestration](14_cognitive_tempo_orchestration.md)**: bounded external scaffolding / interface lane.
