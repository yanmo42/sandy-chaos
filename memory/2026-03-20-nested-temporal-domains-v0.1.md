# Nested Temporal Domains v0.1

## Intent
Capture a Sandy-Chaos-native framing for multiscale interaction that can relate:

- observer / observed coupling,
- chaser / chased pursuit asymmetry,
- parent / child or branch / spine continuity,
- fast / meso / slow update cadences.

The aim is to introduce a cleaner architecture without weakening the project's causal discipline.

---

## Core proposal

Treat each domain as indexed by:

1. **role polarity**
2. **temporal band**

Example index:

`D_{r,k}` where `r` is role and `k` is tempo band.

Allowed transfers are neighbor-first:

- **polarity coupling**: opposite role, same band
- **temporal coupling**: same role, adjacent band

Disallow direct all-to-all coupling by default.

---

## Hard rule

**No raw cross-domain state access.**

Domains may only exchange constrained encodings with explicit:

- latency,
- distortion / loss,
- confidence,
- provenance,
- reconstruction limits.

This keeps the concept aligned with:

- bounded-now access,
- causal-admissible retrodiction,
- partial observability,
- Sandy Chaos claim-tier discipline.

---

## Why this fits Sandy Chaos

The repo already contains the ingredients:

- `docs/02_tempo_tracer_protocol.md` — timing asymmetry / transport metrics
- `docs/03_micro_observer_agency.md` — read-write observer coupling
- `docs/04_neuro_roadmap.md` — fast / meso / slow loop structure
- `docs/05_hyperstition_temporal_bridge_analysis.md` — observer-indexed temporal ordering
- `docs/12_yggdrasil_continuity_architecture.md` — cadence as part of continuity design

Nested Temporal Domains supplies the missing coupling grammar between those pieces.

---

## Claim tiers

### Defensible now
- Sandy Chaos already uses multi-timescale framing and bounded observer language.
- Adjacent-layer encoded transfer is a safer and clearer framing than implicit all-to-all interaction.
- The architecture can be expressed without altering the causal boundary.

### Plausible but unproven
- The concept may improve both explanation quality and experiment design.
- Neighbor-layer transfer models may outperform looser multiscale descriptions in toy systems.

### Speculative
- The architecture may eventually unify physics/cognition/narrative/continuity threads at a deeper level.

---

## Failure conditions

- every layer can talk directly to every other layer,
- no transfer loss model is declared,
- latency/temporal contact is ignored,
- metaphor does mechanism's job,
- speculative language silently becomes policy.

---

## Proposed promotion

Disposition: `DOC_PROMOTE`

Repo changes to pair with this note:

- create canonical doc `docs/13_nested_temporal_domains.md`
- blend the concept into blueprint / glossary / roadmap / continuity docs
- add a research backlog hook for benchmarking neighbor-layer transfer

---

## Immediate next experiments

1. Compare neighbor-only vs all-to-all vs uncoupled multiband toy systems.
2. Define a minimal `TransferBundle` for cross-band summaries.
3. Test reconstruction quality as a function of compression, noise, and latency.
4. Map tempo-chase doctrine into explicit role/band indices.
