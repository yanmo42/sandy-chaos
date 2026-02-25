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

$$
x_{t+\Delta} = F_\Delta(x_t, a_t, \eta_t)
$$

---

## 4) Structural back-propagation vs retrocausality

### Plain language

Future-like informational effects can arise from **boundary-condition propagation** in continuous media.  
In a subcritical flow, mass/entropy move downstream, while pressure/standing-wave signatures from a downstream obstacle can propagate upstream.

An upstream micro-observer can read downstream structure from local gradients without any backward-time channel. The appearance of “retro” influence is therefore geometric/informational, not ontic retrocausation.

### Minimal formalization

Let $q(x,t)$ be a structural-information field on a directed domain $x\in[0,L]$ with downstream boundary at $x=L$:

$$
\partial_t q + u\,\partial_x q = D\,\partial_{xx} q + \eta(x,t),
\qquad q(L,t)=B(t)
$$

Subcritical condition:

$$
Fr=\frac{u}{\sqrt{gh}}<1 \quad\Rightarrow\quad c_{up}=\sqrt{gh}-u>0
$$

So downstream boundary structure $B(t)$ can influence upstream positions after finite forward delay:

$$
q(x_u,t)=\mathcal{K}\big(B(t-\tau_u),\eta_{[0,t]}\big),
\qquad \tau_u=\frac{L-x_u}{c_{up}}>0
$$

Micro-observer/system update is local-gradient driven:

$$
s_{t+\Delta}=\Pi\big(s_t,\nabla q(x_s,t),\zeta_t\big)
$$

No update term requires injecting future-time values into present-time dynamics.

### Causal safety test

$$
P(s_t\mid do(B_{t+\Delta}=b),\mathcal{I}_t)=P(s_t\mid\mathcal{I}_t)
$$

If this holds, there is no ontic backward causal arrow — only forward propagation of structural constraints.

---

## 5) Philosophical lens (without dropping rigor)

The key shift is from **“Can the future act on the past?”** to  
**“How do downstream structures become legible upstream under forward dynamics?”**

This is a framework of local response under global constraint:

- not determinism,
- not mystical retro-action,
- but systems adapting to local gradients produced by boundary geometry.

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