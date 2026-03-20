# 03 Micro-Observer & Agency

## 1) Purpose

This layer describes how observation, interpretation, and action couple at local scale.

If **[02 Tempo Tracer Protocol](02_tempo_tracer_protocol.md)** measures channel transport and **[11 Potential-Flow Contracts](11_geodesic_hydrology_contracts.md)** scores resulting trajectories, this document defines the **observer-coupling layer**: how humans, machines, and hybrids change what is seen and what is done.

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

### 2.1 Mapping the local state model into the shared layer

For notation consistency across **02 / 03 / 11**, this local decomposition should be read as one observer-centric chart of the shared augmented state:

$$
z_t \sim (L_t, O_t, S_t, A_t, h_t)
$$

Where:

- $L_t$ is the latent environment component,
- $O_t$ is the observed / measured slice,
- $S_t$ is the observer-internal state,
- $A_t$ is the intervention / control component,
- $h_t$ collects any additional memory variables needed for path dependence.

Under this mapping:

- the shared transport geometry $(g, K)$ constrains how future updates can propagate,
- the observer-coupling term $B_\lambda$ acts mainly through the $S_t$ and $A_t$ channels,
- Tempo Tracing later reads out directional asymmetry over $\Delta\tau$,
- and Potential-Flow Contracts score trajectories through this augmented state space.

So this document is not using a conflicting ontology; it is using a more fine-grained observer-local coordinate system for the same forward-causal framework.

---

## 3) Read-write observer effect

In this framework, observation is **read-write coupling**:

- **Read**: infer latent structure
- **Write**: alter future structure via measurement policy, framing, and feedback

Compactly:

$$
\Delta L_t \propto \Phi(S_t, \text{measurement policy}, \text{feedback loop})
$$

Under the operational-present axioms (N1–N3), the observer update channel is latency-bounded and policy-conditioned:

$$
y_i(\tau_i)=\mathcal{M}_i\big(x_{t-\delta_i},\pi_i\big)+\epsilon_i
$$

This means the observer never has direct access to a global instantaneous present; it has delayed/noisy evidence streams whose interpretation depends on policy.

In the shared formal layer used across **02 / 03 / 11**, this observer term is best understood as a bounded forcing/control contribution inside the transport law:

$$
\dot{z}_t = -K_{z_t}\,\mathrm{grad}_g H(z_t,t) + B_\lambda(z_t,t)
$$

Where:

- $H$ is the head / potential field defined at the contract layer,
- $g$ and $K$ define the weighted transport geometry,
- $B_\lambda$ is the observer-coupling term defined here,
- and Tempo Tracing measures the resulting directional asymmetries over $\Delta\tau$.

This keeps the role of agency precise:

- observer coupling does **not** mean a backward-causal signal,
- it does **not** yet mean a learned universal potential field,
- it means present-step measurement, framing, and feedback alter **future admissible transport** in a bounded, measurable way.

This unifies physical, cognitive, and socio-technical observer effects under one formal language.

When the same observer/control process is modeled across fast, meso, and slow bands, Sandy Chaos should treat those bands as **adjacent nested temporal domains** rather than as a flat stack with unrestricted access. In that reading, each band exchanges bounded encodings with its neighbors, not raw omniscient state. See **[13 Nested Temporal Domains](13_nested_temporal_domains.md)** for the cross-cutting architecture.

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

This is **epistemic retro-influence**, not physical retrocausality, and corresponds to N3 causal admissibility in the operational-present axioms.

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
- **[11 Potential-Flow Contracts](11_geodesic_hydrology_contracts.md)** for the head-field and path-functional contract layer built on top of observer-coupled transport.
- **[Math Appendix](math_appendix.md)** for compact equation reference.


## 10) Updated implementation direction (2026-03)

To make agency a computed physical consequence (not an add-on), this layer now uses a concrete observer coupling term already implemented in simulation.

In the shared formal layer, this is the operational realization of the bounded forcing term $B_\lambda$:

$$
B_\lambda(x,t) \equiv \Phi(x,t)=\sum_i \lambda\,G_i(x)\,[r_i m_i(t)+w_i f_i(t)]\,\hat{u}_i(x)
$$

Where:

- $G_i(x)$ is a bounded spatial kernel around probe $i$,
- $m_i(t)$ is read-memory (smoothed local measurement),
- $f_i(t)$ is write-feedback from observer state,
- $(r_i,w_i)$ are read/write gains,
- $\lambda$ is a global coupling scale.

This keeps strict forward causality: measurements and feedback at $t$ perturb only future updates.

Important scope note: the current implementation realizes observer coupling primarily as a **forcing / steering term** $B_\lambda$. It does **not** yet implement a full learned deformation of the head field $H$ itself. That distinction matters for keeping the present claim level honest.

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

