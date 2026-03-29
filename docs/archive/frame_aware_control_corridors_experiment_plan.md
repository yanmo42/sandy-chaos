# Frame-Aware Control Corridors — Experiment Plan v0.1

> **Status:** exploratory experiment design.
>
> This document translates `frame_aware_control_corridors.md` into a minimal falsifiable simulation plan. The goal is not to prove exotic propulsion or gravity engineering. The goal is to test whether **frame-aware coordination under delay and clock mismatch** creates a measurable control advantage over simpler baselines.

Related docs:

- `docs/archive/frame_aware_control_corridors.md`
- `docs/02_tempo_tracer_protocol.md`
- `docs/03_micro_observer_agency.md`
- `docs/13_nested_temporal_domains.md`

---

## 1) Core experimental question

Can a **frame-aware corridor controller** maintain a vehicle inside a low-cost admissible trajectory family more effectively than:

1. **local-only control**, and
2. **delay-ignorant remote control**,

when the system is subject to:

- propagation delay,
- clock mismatch,
- bounded state-reconstruction error,
- and simple environmental geometry?

This is the first useful question. It is intentionally narrower than any claim about "gravitational control."

---

## 2) Null model and competitor models

### Model A — Local-only control (null baseline)

The vehicle uses only onboard sensing and local policy.

Characteristics:
- no relay or remote estimates,
- no corridor packet exchange,
- no frame translation burden.

Interpretation:
- baseline autonomous guidance.

### Model B — Delay-ignorant remote control

A remote controller sends guidance using stale estimates as if they were current.

Characteristics:
- remote support exists,
- propagation delay exists,
- clock mismatch exists,
- but the policy does **not** compensate for either.

Interpretation:
- naive networked control.

### Model C — Frame-aware corridor control

A remote/meso controller sends guidance packets whose use is conditioned on:

- propagation delay,
- clock mismatch,
- validity window,
- and bounded local state reconstruction.

Interpretation:
- same basic information path as Model B, but with temporal discipline.

---

## 3) Minimal toy system

Keep the system small.

### Actors
- **Vehicle** — local controller + local state estimate
- **Remote controller** — emits corridor guidance packets
- **Optional relay/observer** — may be added in v0.2, but not required for v0.1

### State space
Use a 2D kinematic toy vehicle with:

- position: $(x_t, y_t)$
- velocity: $(v_{x,t}, v_{y,t})$
- control input: $(u_{x,t}, u_{y,t})$

A simple discrete update is sufficient:

$$
\mathbf{p}_{t+1} = \mathbf{p}_t + \mathbf{v}_t \Delta t
$$

$$
\mathbf{v}_{t+1} = \mathbf{v}_t + \mathbf{u}_t \Delta t + \mathbf{d}_t
$$

Where $\mathbf{d}_t$ is a bounded disturbance term.

### Environment geometry
The vehicle should be asked to remain near a corridor centerline or tube.

Minimal version:
- one curved path or spline,
- one corridor width parameter $w$,
- optional hazard regions or curvature spikes.

The environment should make control nontrivial but still interpretable.

---

## 4) Corridor object

Use the corridor as a geometric and control object, not as a literal force field.

Minimal corridor representation:

$$
\mathcal{C} = \{\gamma(s),\; w,\; v_{ref}(s),\; validity\_window\}
$$

Where:

- $\gamma(s)$ = centerline curve,
- $w$ = admissible corridor half-width,
- $v_{ref}(s)$ = reference velocity profile,
- `validity_window` = time window in which the corridor packet should be trusted.

A corridor packet may carry:

$$
P_{corr} = \{s_{target},\; \hat{x},\; \hat{v},\; confidence,\; validity\_window\}
$$

This is enough for v0.

---

## 5) Variables to sweep

Keep the sweep small and interpretable.

### Primary variables

1. **Propagation delay**

$$
\delta_{prop}
$$

2. **Clock mismatch**

$$
\delta_{clock}
$$

3. **Reconstruction error**

$$
\epsilon_{recon}
$$

4. **Corridor width**

$$
w
$$

### Optional later variables
- disturbance amplitude,
- packet drop rate,
- validity-window shrinkage,
- relay count.

For v0.1, do **not** introduce all of these at once.

---

## 6) Core metrics

### 6.1 Corridor effectiveness

Primary metric:

$$
\Gamma_{corridor} = 1 - \frac{1}{T}\sum_{t=1}^{T} \min\left(1, \frac{d(\mathbf{p}_t, \gamma)}{w}\right)
$$

Interpretation:
- near 1 = vehicle stays near the corridor centerline,
- near 0 = vehicle frequently exits or rides the edge badly.

### 6.2 Control effort

$$
J_u = \frac{1}{T}\sum_{t=1}^{T} \|\mathbf{u}_t\|^2
$$

Interpretation:
- how much actuation cost is required to maintain route quality.

### 6.3 Violation rate

$$
V_{out} = \frac{1}{T}\sum_{t=1}^{T} \mathbf{1}[d(\mathbf{p}_t, \gamma) > w]
$$

Interpretation:
- fraction of time outside corridor bounds.

### 6.4 Freshness / validity usage

Track the fraction of remote packets that are:
- applied while still valid,
- applied stale,
- rejected for expiry.

This is important because otherwise the frame-aware model can cheat by silently ignoring timing burden.

---

## 7) Predictions

### Defensible prediction

As $\delta_{prop}$ and $\delta_{clock}$ increase:
- Model B (delay-ignorant remote control) should degrade faster than Model A or C.

### Plausible prediction

There exists a regime where Model C achieves:
- higher $\Gamma_{corridor}$ than Model A,
- lower $V_{out}$ than Model B,
- and comparable or lower actuation cost than naive remote control.

### More specific hypothesis

For moderate delay and moderate clock mismatch:

$$
\Gamma_C > \Gamma_A \quad \text{and} \quad \Gamma_C > \Gamma_B
$$

with the strongest advantage appearing when remote estimates remain useful but only if validity windows are respected.

---

## 8) Failure conditions

The corridor concept should be considered weak or misleading if any of the following happen:

1. **No advantage over simpler control**
   - Model C does not outperform Model A or B in any meaningful regime.

2. **Equivalent to ordinary latency compensation**
   - all corridor language collapses into a standard stale-state controller with no additional explanatory value.

3. **Metric non-discrimination**
   - $\Gamma_{corridor}$ does not distinguish good vs bad regimes better than a trivial distance-to-path metric.

4. **Success requires hand-tuned oracle knowledge**
   - Model C only works if it receives unrealistically accurate future-like state estimates.

5. **The concept encourages overclaiming**
   - users begin reading corridor success as evidence for literal field shaping or gravity engineering.

If those happen, keep the idea in archive space or rename it more narrowly.

---

## 9) Minimal implementation plan

### v0.1 files

Recommended first implementation targets:

- `scripts/frame_aware_corridor_sim.py`
- `tests/test_frame_aware_corridor_sim.py`
- `memory/frame-aware-corridor-experiment-v0.1.md` or research-cycle artifacts under `memory/research/`

### Script requirements

The simulation script should:
- run all three models,
- accept sweep parameters,
- output a compact CSV/JSON summary,
- optionally produce one plot of corridor effectiveness vs delay.

### Test requirements

The first tests should check:

1. zero-delay sanity case
   - Model B and C should reduce toward similar behavior when delay and mismatch vanish.

2. stale-control degradation
   - Model B should degrade as delay increases.

3. validity-window discipline
   - Model C should reject or downweight stale packets.

4. corridor metric sanity
   - clear off-corridor trajectories should score worse than stable in-corridor ones.

---

## 10) Suggested experiment matrix

Keep the first matrix tiny.

### Sweep 1 — delay only
- fix clock mismatch near zero
- vary $\delta_{prop}$ from low to moderate
- compare A/B/C on $\Gamma_{corridor}$, $V_{out}$, $J_u$

### Sweep 2 — delay + clock mismatch
- fix corridor width
- vary $\delta_{prop}$ and $\delta_{clock}$ jointly
- identify boundary where naive remote control collapses

### Sweep 3 — validity window ablation
- hold delay constant
- vary packet validity window
- check whether explicit temporal discipline matters or is decorative

Do **not** add relays, hazards, or swarm consensus until at least one of these produces interpretable structure.

---

## 11) Promotion criteria

This work should only move beyond archive status if at least one of the following happens:

1. The frame-aware controller shows a reproducible advantage over both baselines in a nontrivial regime.
2. The corridor metric provides explanatory value not captured by a simpler one-line path-tracking score.
3. The toy simulation reveals a structurally interesting failure boundary that maps cleanly onto Tempo Tracer / Nested Temporal Domains language.

If not, the concept should remain a useful cautionary vocabulary note rather than a promoted research direction.

---

## 12) Recommended next concrete action

Implement the smallest possible v0.1 simulation with:

- one 2D vehicle,
- one curved corridor,
- one remote controller,
- propagation delay,
- clock mismatch,
- packet validity windows,
- and the three competitor models A/B/C.

That is the narrowest experiment that can tell us whether "frame-aware control corridor" is a meaningful object or merely good naming.
