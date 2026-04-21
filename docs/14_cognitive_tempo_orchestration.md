# 14 Cognitive Tempo Orchestration

> **Status:** canonical near-term architecture / interface roadmap.
>
> This document promotes the strongest defensible part of the older implant-orchestration line into the canonical Sandy Chaos path. It defines **Cognitive Tempo Orchestration (CTO)** as a bounded, auditable, human-in-the-loop approach for improving alignment between goals, state, and action by shaping external conditions rather than claiming invasive or coercive write-access to the person.
>
> Related docs:
>
> - `docs/03_micro_observer_agency.md`
> - `docs/04_neuro_roadmap.md`
> - `docs/05_hyperstition_temporal_bridge_analysis.md`
> - `docs/07_agentic_automation_loop.md`
> - `docs/12_yggdrasil_continuity_architecture.md`
> - `docs/13_nested_temporal_domains.md`
>
> Claim posture:
>
> - **Defensible now:** external timing, interface scaffolding, pacing, salience management, and bounded feedback can measurably change readiness, task continuity, and cross-tempo alignment.
> - **Plausible but unproven:** a disciplined orchestration layer can improve execution quality without increasing coercion, overload, or dependence.
> - **Speculative:** a mature CTO stack could eventually interoperate with richer latent-state estimation or neural-interface systems, but that stronger claim should not do present-day mechanism work.

---

## 1) Why this doc exists

Sandy Chaos has developed a much stronger multiscale architecture for cognition and agency than the older canonical path makes explicit.

The repo now has three distinguishable lanes:

1. **Neural evidence / decoding lane**
   - what can be measured or inferred from neural signals under bounded conditions.
2. **Multiscale architecture lane**
   - how fast / meso / slow domains exchange constrained summaries.
3. **External orchestration lane**
   - how prompts, pacing, task framing, interface timing, and environmental cues can improve action readiness without violating the agency boundary.

This document formalizes the third lane.

The core rule is simple:

> **shape the potential landscape, not the person's final act.**

That preserves the project's agency discipline while making the near-term roadmap more actionable.

---

## 2) Plain-language definition

**Cognitive Tempo Orchestration (CTO)** is a bounded control layer that attempts to improve alignment between:

- slow goals,
- meso-level task routing and context,
- and fast action opportunities,

by adjusting **external conditions** such as:

- prompt timing,
- notification cadence,
- task chunking,
- salience ordering,
- interface friction,
- environment cues,
- and reflection/review cadence.

CTO does **not** claim:

- mind control,
- direct authorship of action,
- unrestricted access to internal state,
- or ethically valid hidden coercion.

The person remains the final initiator.

---

## 3) Relationship to Nested Temporal Domains

CTO is easier to state cleanly once Sandy Chaos adopts **Nested Temporal Domains** as its coupling grammar.

In CTO terms:

- **fast domain** = immediate prompts, action windows, overload guards, interruption control,
- **meso domain** = task routing, session framing, chunking, state estimation, summary handoff,
- **slow domain** = goals, identity consistency, policy constraints, preference continuity.

The hard architectural rule still applies:

> domains exchange bounded, neighbor-layer representations rather than raw omniscient state.

So CTO should not be described as a system that fully knows the user's internal state.
It should be described as a system that:

- observes partial external traces,
- forms bounded estimates,
- and applies constrained interventions across adjacent tempo bands.

### 3.1 Cadence mapping onto edge / bridge / spine

For continuity with `docs/12_yggdrasil_continuity_architecture.md`, the three CTO loops map onto the canonical Yggdrasil cadence surfaces:

- **fast = edge** cadence → safety, rate limiting, and reversible local modulation,
- **meso = bridge** cadence → state scaffolding, routing, and cross-band summary handoff,
- **slow = spine** cadence → continuity, identity constraints, and policy shaping.

The mapping stays strictly forward-causal: edge observations can inform bridge summaries, and bridge summaries can justify spine revisions, but CTO should not imply direct fast-to-spine promotion or any retrocausal rewrite of slow-band policy from raw fast-loop activity.

---

## 4) Core architecture

### 4.1 Fast loop — safety and rate limiting

Role:
- prevent overload,
- prevent compulsive escalation,
- preserve reversibility.

Typical mechanisms:
- burst throttling,
- interruption budgets,
- notification dampening,
- emergency quiet mode,
- anti-pile-on rules.

Primary failure mode:
- the system becomes stimulating faster than the user can metabolize.

### 4.2 Meso loop — state scaffolding and routing

Role:
- estimate actionable readiness from observable traces,
- choose the next useful framing,
- stage tasks so that the fast loop sees tractable action windows.

Typical inputs:
- response latency,
- task switching frequency,
- correction rate,
- backlog shape,
- schedule context,
- explicit user feedback,
- optional wearable or ambient proxies if available.

Typical outputs:
- reordered prompts,
- chunked next steps,
- timing-adjusted nudges,
- salience emphasis,
- bounded environment changes.

### 4.3 Slow loop — continuity and identity constraints

Role:
- ensure short-horizon optimization stays subordinate to user-authored meaning.

Typical functions:
- long-term goal checking,
- preference drift detection,
- autonomy audits,
- cadence reviews,
- continuity summaries.

This is where CTO should remain answerable to explicit human intent rather than optimizing a narrow engagement proxy.

---

## 5) Minimal packet / contract view

A useful abstract object is a **state-targeting orchestration packet**:

$$
P_{cto} = \{\vec{S}_{target},\; \tau_{ramp},\; \mathcal{I}_{allowed},\; Budget_{attn},\; confidence,\; provenance,\; validity\_window\}
$$

Interpretation:

- $\vec{S}_{target}$ = desired coarse state direction (for example calm focus, lower switching, higher initiation readiness),
- $\tau_{ramp}$ = allowed transition time constant,
- $\mathcal{I}_{allowed}$ = permitted intervention classes,
- $Budget_{attn}$ = attentional / affective perturbation budget,
- `confidence` = estimator confidence,
- `provenance` = why the recommendation exists,
- `validity_window` = when it should still be considered usable.

The packet should never mean:
- “perform action X now.”

It should mean:
- “shape conditions toward state Y within declared bounds.”

---

## 6) Safety invariants

CTO is invalid if these cannot be enforced.

1. **Cut-cord principle**
   - the user can disable or neutralize the orchestration layer immediately.

2. **No action forcing**
   - the system may scaffold probabilities, not author irreversible acts on the person's behalf.

3. **Transparency of pressure**
   - the user can inspect why a modulation occurred and how much pressure is currently being applied.

4. **Counterfactual traceability**
   - the system should expose what changed, what it was trying to improve, and uncertainty around the estimate.

5. **Preference drift audits**
   - repeated short-term optimizations must not silently rewrite identity-level goals.

6. **Bounded intervention energy**
   - prompts, salience, and timing changes must be capped and decay when signals weaken.

---

## 7) What is defensible vs speculative

### Defensible now
- External timing and interface structure can affect readiness, friction, and continuity of action.
- Human-in-the-loop prompting systems can improve execution in bounded tasks.
- Overload, dependence, and coercion risks are real and should be treated as first-class failure conditions.

### Plausible but unproven
- A properly instrumented CTO layer could improve cross-tempo alignment between stated goals and realized actions.
- Neighbor-band orchestration may outperform flat reminder spam or purely reactive assistant behavior.

### Speculative
- CTO could eventually interoperate with richer latent-state or neural decoding systems.
- High-fidelity state scaffolding could become a new communication / cognition interface class.

---

## 8) Validation and falsification

CTO should live or die on measured outcomes.

### Core metrics
- task initiation lift,
- task completion / continuation lift,
- reduced harmful switching,
- calibration of readiness estimates,
- overload incidence,
- dependence / autonomy drift,
- user-rated helpfulness vs annoyance.

### Failure conditions
- no reproducible gain over simpler reminder baselines,
- high-confidence bad nudges,
- rising overload or avoidance,
- visible dependence growth,
- hidden optimization pressure the user cannot inspect or stop.

If these appear, the orchestration policy should be revised or withdrawn.

---

## 9) Relationship to repo implementation

CTO is not yet a finished product surface. It is a canonical framing that aligns current work more honestly.

Current repo strengths already support parts of this lane:

- bounded observer language,
- multiscale fast / meso / slow framing,
- temporal asymmetry metrics,
- continuity cadences,
- falsification-first protocol design.

What remains open:

- explicit orchestration-policy simulations,
- benchmark suites against naive reminder baselines,
- overload / dependence metrics,
- transfer objects for cross-band summaries,
- operational UI/UX prototypes.

---

## 10) Summary

Cognitive Tempo Orchestration gives Sandy Chaos a practical near-term lane for turning its multiscale architecture into actionable interface design.

The core commitments are:

- preserve the agency boundary,
- shape conditions rather than steal action,
- keep interventions bounded and auditable,
- couple fast / meso / slow layers through constrained summaries,
- and benchmark the system against simpler alternatives.

If the lane works, it becomes a rigorous bridge between theory and real execution support.
If it fails, it should fail cleanly by showing that the added orchestration structure does not outperform simpler, more honest systems.
