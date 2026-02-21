# 01 Foundations

## 1) Purpose

Sandy Chaos studies **future-like informational effects** under strict causal discipline.  
The goal is not to prove backward-time messaging. The goal is to formalize when temporal asymmetry, inference, and protocol design can produce forecasting advantage without violating physics.

---

## 2) Claim discipline

We keep three explicit tiers:

- **Defensible now**: causality-preserving signaling, retrodiction from later observables, observer-dependent timing asymmetries, falsification metrics.
- **Plausible but unproven**: stronger cross-frame decoding robustness, stable multi-agent anticipatory coordination.
- **Speculative**: high-fidelity cognition transfer, deep ontological claims.

This separation is method, not branding.

---

## 3) Non-negotiable causality boundary

1. No superluminal messaging.
2. No operational closed timelike curve claim.
3. No physical channel from future state to past event.
4. Any “future-like” advantage must be attributable to timing asymmetry + inference.

Forward state dynamics remain:

\[
x_{t+\Delta} = F_\Delta(x_t, a_t, \eta_t)
\]

---

## 4) Retrodictive transparency vs retrocausality

### Plain language

Future observers may infer what happened in the past with very high precision.  
That can change present behavior **because people know they will be inferable**.

This creates a strong *appearance* of backward influence, but causality is still forward-only.

### Minimal formalization

Retrodiction map:

\[
\hat{a}_t = R(x_{t+\Delta}), \qquad P(\hat{a}_t = a_t) \approx 1
\]

Anticipatory policy (present agent optimizing under expected future inference):

\[
a_t^* = \arg\max_a\;\mathbb{E}\big[U(a, \Psi(R(F_\Delta(x_t,a,\eta_t))))\mid \mathcal{I}_t\big]
\]

Where \(\mathcal{I}_t\) is present information about the future observers’ capabilities.

### Causal safety test

\[
P(a_t\mid do(x_{t+\Delta}=z),\mathcal{I}_t)=P(a_t\mid\mathcal{I}_t)
\]

If this holds, there is no ontic backward causal arrow.

---

## 5) Philosophical lens (without dropping rigor)

The key shift is from **“Can the future act on the past?”** to  
**“How does anticipated future legibility reshape present agency?”**

This is a framework of responsibility under inferability:

- not determinism,
- not mystical retro-action,
- but strategic self-positioning inside a known inferential ecosystem.

---

## 6) What would falsify the framing

- Evidence requiring superluminal propagation to explain observed effects.
- Claimed influence that cannot be reduced to forward dynamics + information state.
- Non-reproducible gains once baseline inference and noise controls are applied.

---

## 7) Read next

- **[02 Tempo Tracer Protocol](02_tempo_tracer_protocol.md)** for channel mechanics and falsification metrics.
- **[03 Micro-Observer & Agency](03_micro_observer_agency.md)** for observer coupling and ethics.
- **[Glossary](glossary.md)** for consistent terminology.