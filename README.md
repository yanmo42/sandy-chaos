# Sandy Chaos

Focused sandbox for exploring **Tempo Tracer**: causality-preserving, relativistic communication ideas using curved-spacetime photon dynamics and nested-time protocol abstractions.

## Primary docs

- **[Tempo Tracer framework](docs/tempo_tracer.md)** ← main conceptual/spec document
- **[Micro-Observer Framework](docs/micro_observer_framework.md)** ← local-scale observer/consciousness/agency modeling layer
- **[Neuromorphic Cross-Tempo Architecture](docs/neuromorphic_cross_tempo_architecture.md)** ← neuroscience-aligned timing/control formalization
- **[Neuro-Implant Cross-Tempo Brainstorm](docs/neuro_implant_cross_tempo_brainstorm.md)** ← speculative-but-grounded implant extension

## Repository modules

- `cosmic_comm/`: Kerr metric + geodesic tracing prototypes
- `nfem_suite/`: simulation + protocol + visualization stack

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
- **Speculative extensions** (future engineering scenarios)

See `docs/tempo_tracer.md` for assumptions, constraints, and falsification metrics.

## License

MIT License — See [LICENSE](LICENSE)

---

## Disclaimer

This repo is more of an intellectual exercise, to see if the math can be written to support the physical ideas
