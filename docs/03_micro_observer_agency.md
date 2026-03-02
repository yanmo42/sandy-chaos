# 03 Micro-Observer & Agency

## 1) Purpose

This layer describes how observation, interpretation, and action couple at local scale.

If Tempo Tracer is the channel geometry, this document is the **observer geometry**: how humans, machines, and hybrids change what is seen and what is done.

---

## 2) Core state model

We model interaction with four state families:

- $L_t$: latent environment state
- $O_t$: observed state
- $S_t$: observer state (memory, priors, attention, self-model)
- $A_t$: intervention/action state

Minimal dynamics:

$$
O_t = \mathcal{M}(L_t, S_t, \epsilon_t),
\qquad
L_{t+1} = \mathcal{T}(L_t, A_t, \eta_t)
$$

Observation is not purely passive: measuring changes future measurability.

---

## 3) Read-write observer effect

In this framework, observation is **read-write coupling**:

- **Read**: infer latent structure
- **Write**: alter future structure via measurement policy, framing, and feedback

Compactly:

$$
\Delta L_t \propto \Phi(S_t, \text{measurement policy}, \text{feedback loop})
$$

This unifies physical, cognitive, and socio-technical observer effects under one formal language.

---

## 4) Agency and communicator types

An entity has operational agency if it can:

1. choose policies,
2. evaluate outcomes,
3. update policy relative to internal objectives.

Communicators may be:

- **Intentional** (explicit signal encoding)
- **Incidental** (behavior carries signal content unintentionally)
- **Machine-mediated** (algorithmic layers filter/amplify/align)

---

## 5) Structural coupling without retrocausality

This is where the key distinction lives at micro scale:

- downstream/topological structure can become locally legible upstream,
- present systems update from local gradients carrying that structural information.

That is **epistemic retro-influence**, not physical retrocausality.

Gradient-coupled view:

$$
s_{t+\Delta}=\Pi\big(s_t,\nabla q(x_s,t),\zeta_t\big)
$$

The update depends on present local state and local field geometry, not on a backward causal signal.

---

## 6) Consciousness as operational proxies

We avoid metaphysical closure and use measurable proxy dimensions:

- $B$: attention bandwidth
- $D$: temporal integration depth
- $C$: self-coherence
- $R$: reflective recursion

Optional index:

$$
\chi = f(B,D,C,R)
$$

$\chi$ is descriptive, not a value ranking.

---

## 7) Ethical invariants

Any deployment involving cognition or agency must preserve:

1. **Consent**
2. **Transparency**
3. **Reversibility**
4. **Auditability**
5. **Autonomy preservation**

If these fail, performance gains do not legitimize the system.

---

## 8) What counts as progress vs failure

Progress indicators:

- improved calibration between machine forecasts and human judgment,
- lower cross-frame interpretation error,
- improved long-horizon coherence without agency loss.

Failure indicators:

- dependence growth with reduced user-directed revision,
- opaque influence pathways,
- short-term compliance gains with long-term coherence decline.

---

## 9) Read next

- **[04 Neuro Roadmap](04_neuro_roadmap.md)** for staged implementation strategy.
- **[Math Appendix](math_appendix.md)** for compact equation reference.


## 10) Updated implementation direction (2026-03)

To make agency a computed physical consequence (not an add-on), this layer now uses a concrete observer coupling term already implemented in simulation:

$$
\Phi(x,t)=\sum_i \lambda\,G_i(x)\,[r_i m_i(t)+w_i f_i(t)]\,\hat{u}_i(x)
$$

Where:

- $G_i(x)$ is a bounded spatial kernel around probe $i$,
- $m_i(t)$ is read-memory (smoothed local measurement),
- $f_i(t)$ is write-feedback from observer state,
- $(r_i,w_i)$ are read/write gains,
- $\lambda$ is a global coupling scale.

This keeps strict forward causality: measurements and feedback at $t$ perturb only future updates.

### Agency observables now computed in-code

The simulation now exports three forward-causal agency observables from `ObserverCoupling.collect_step_stats(...)`:

- **`intervention_gain`**: normalized realized actuation strength,
  \(\mathrm{clip}(\mathbb{E}[\|\Phi\|]/\Phi_{\max}, 0, 1)\). 
- **`counterfactual_control_score`**: write-channel share of present control effort,
  \(\mathbb{E}[\,|w_i f_i|/(|r_i m_i| + |w_i f_i| + \varepsilon)\,]\). 
- **`predictive_horizon`**: effective forward-looking persistence (in update steps),
  \((1-\mathrm{decay})^{-1} \cdot \mathbb{E}[\mathrm{temporal\_frame\_scale}]\). 

All three are computed from present-step measurements/state and characterize only future update influence (no retrocausal interpretation).

Dashboard instrumentation now also tracks two causal traces for operator visibility:
- **`observer_coupling_drift`**: stepwise change in realized coupling magnitude,
  
  \(|\mathbb{E}[\|\Phi\|]_t - \mathbb{E}[\|\Phi\|]_{t-1}|\).
- **`frame_channel_asymmetry`**: integrated directional communication gap,
  
  \(\sum_{\Delta\tau}\,|\mathcal{A}(\Delta\tau)|\), where
  \(\mathcal{A}(\Delta\tau)=C_{A\to B}(\Delta\tau)-C_{B\to A}(\Delta\tau)\).

### Claim tiers for the Agency + Temporal Communication buildout (2026-03)

**Defensible (implemented + testable now)**

- The observer-coupling term \(\Phi(x,t)\) is a forward-causal control input: present-step read/write signals influence only future state updates.
- `intervention_gain`, `counterfactual_control_score`, and `predictive_horizon` are computable operational observables (produced per step from present state/measurements).
- Directional frame communication metrics \(C_{A\to B}(\Delta\tau)\), \(C_{B\to A}(\Delta\tau)\), and asymmetry \(\mathcal{A}(\Delta\tau)\) are measurable diagnostics of communication imbalance under the modeled coupling.
- Null-vs-coupled comparison can falsify "no directional effect" claims: if asymmetry disappears under controls, the stronger coupling interpretation fails.

**Speculative (explicitly non-evidentiary at present)**

- Any claim that these observables imply consciousness, intent, or intrinsic agency beyond the defined operational metrics.
- Any metaphysical reading (including panpsychic or ontological interpretations) not anchored to reproducible measurement protocols.
- Any claim that frame asymmetry constitutes physical backward-time signaling.

**Disallowed interpretation boundary**

- No retrocausal claims: observed forecasting advantage is interpreted as forward-causal lead-time generated by structure + update dynamics, not influence from future states.

