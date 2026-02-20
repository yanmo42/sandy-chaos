# Sandy Chaos

Focused sandbox for exploring **Temporal Hacks**: causality-preserving, relativistic communication ideas using curved-spacetime photon dynamics and nested-time protocol abstractions.

## Primary docs

- **[Temporal Hacks framework](docs/temporal_hacks.md)** ← main conceptual/spec document

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

See `docs/temporal_hacks.md` for assumptions, constraints, and falsification metrics.

## License

MIT License — See [LICENSE](LICENSE)

---

## Disclaimer

This repo is more of an intellectual exercise, to see if the math can be written to support the physical ideas
MIT — see [LICENSE](LICENSE).
