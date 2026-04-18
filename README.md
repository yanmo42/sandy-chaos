# Sandy Chaos

Focused sandbox for exploring **Tempo Tracer**: causality-preserving, relativistic communication ideas using curved-spacetime photon dynamics and nested-time protocol abstractions.

## Documentation

Start here:

- **[Docs index](docs/README.md)** ← reading paths + structure
- **[Spine README](spine/README.md)** ← concept / pressure / promotion governance

Canonical set (compressed):

- **[01 Foundations](docs/01_foundations.md)**
- **[02 Tempo Tracer Protocol](docs/02_tempo_tracer_protocol.md)**
- **[03 Micro-Observer & Agency](docs/03_micro_observer_agency.md)**
- **[04 Neuro Roadmap](docs/04_neuro_roadmap.md)**
- **[13 Nested Temporal Domains](docs/13_nested_temporal_domains.md)**
- **[14 Cognitive Tempo Orchestration](docs/14_cognitive_tempo_orchestration.md)**
- **[17 Endosymbiosis and Host Assimilation](docs/17_endosymbiosis_and_host_assimilation.md)**
- **[18 Adaptive Substrate and Host Binding](docs/18_adaptive_substrate_and_host_binding.md)**
- **[19 Surface Authority Architecture](docs/19_surface_authority_architecture.md)**

Supporting:

- **[Glossary](docs/glossary.md)**
- **[Math Appendix](docs/math_appendix.md)**
- **[Topological Memory Runtime Adoption v0](docs/notes/topological_memory_runtime_adoption_v0.md)**
- **[Implementation Prompts](plans/prompts/README.md)**

Legacy long-form drafts are preserved in **`docs/archive/`**.

## Repository modules

- `cosmic_comm/`: Kerr metric + geodesic tracing prototypes
- `nfem_suite/`: simulation + protocol + visualization stack, including inspectable benchmark scaffolds under `nfem_suite/benchmarks/`

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r nfem_suite/requirements.txt
export PYTHONPATH=$PYTHONPATH:.
python -m nfem_suite.main
```

Optional cosmic tracer demo:

```bash
python -m cosmic_comm.main
```

## Scope discipline

This project intentionally distinguishes between:

- **Defensible claims** (causality-preserving, testable signal structure)
- **Plausible but unproven claims** (promising extensions that still need stronger evidence)
- **Speculative extensions** (future engineering scenarios)

See `docs/01_foundations.md` for assumptions and claim boundaries, `docs/02_tempo_tracer_protocol.md` for constraints + falsification metrics, and `docs/19_surface_authority_architecture.md` for surface/authority discipline.

## Implementation prompt loop

Sandy Chaos now treats some docs as sources for bounded implementation pressure rather than as decorative theory.

Start here:
- **[Implementation Prompts](plans/prompts/README.md)**
- **[SC-PROMPT-0001](plans/prompts/SC-PROMPT-0001-topological-memory-runtime-adoption-v0.md)**
- **[Adversarial Review Template](plans/prompts/review_template_adversarial.md)**

The loop is:
- canonical docs -> prompt packet -> code/tests/evidence -> adversarial review -> promotion or revision

## Spine governance

Sandy Chaos now includes a lightweight **spine** under `spine/`.

The spine tracks:
- **concept nodes** — what meaningful ideas/units currently exist
- **pressure events** — what happened when those concepts were challenged or evaluated
- **promotion events** — what became more durable, moved, merged, or was redirected

This repo is not just a pile of notes and scripts.
It is meant to preserve an inspectable relationship between:
- concepts
- docs
- code
- tests
- evidence
- disposition outcomes

Quick spine commands:

```bash
python3 scripts/spine_report.py
python3 scripts/spine_validate.py
```

## License

MIT License — See [LICENSE](LICENSE)

---

## Disclaimer

This repo is more of an intellectual exercise, to see if the math can be written to support the physical ideas
