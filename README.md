# Sandy Chaos

Focused sandbox for exploring **Tempo Tracer**: causality-preserving, relativistic communication ideas using curved-spacetime photon dynamics and nested-time protocol abstractions.

## Documentation

Start here:

- **[Docs index](docs/README.md)** ← reading paths + structure

Canonical set (compressed):

- **[01 Foundations](docs/01_foundations.md)**
- **[02 Tempo Tracer Protocol](docs/02_tempo_tracer_protocol.md)**
- **[03 Micro-Observer & Agency](docs/03_micro_observer_agency.md)**
- **[04 Neuro Roadmap](docs/04_neuro_roadmap.md)**

Supporting:

- **[Glossary](docs/glossary.md)**
- **[Math Appendix](docs/math_appendix.md)**

Legacy long-form drafts are preserved in **`docs/archive/`**.

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

See `docs/01_foundations.md` for assumptions and claim boundaries, and `docs/02_tempo_tracer_protocol.md` for constraints + falsification metrics.

## License

MIT License — See [LICENSE](LICENSE)

---

## Disclaimer

This repo is more of an intellectual exercise, to see if the math can be written to support the physical ideas
