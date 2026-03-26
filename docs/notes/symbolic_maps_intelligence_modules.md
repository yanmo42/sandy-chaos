# Symbolic Maps Intelligence Modules Roadmap

## Objective

Turn the current Symbolic Maps lane from elegant scaffolding into a usable intelligence substrate.

## Immediate module stack

### 1. Validation
Purpose:
- enforce record integrity
- catch missing fields, duplicates, and bad confidence tiers
- prevent atlas drift into symbolic prose sludge

Surface:
- `validator.py`

### 2. Normalization
Purpose:
- canonicalize operator names
- normalize whitespace, casing, and obvious synonym drift
- make comparison and clustering possible

Surface:
- `normalize.py`

### 3. Composition
Purpose:
- compute operator overlap
- identify compatible and conflicting symbolic combinations
- generate symbolic clusters and archetype blends

Proposed future surface:
- `compose.py`

### 4. Retrieval
Purpose:
- search by operator, role, failure mode, or source domain
- support downstream routing and design tasks

Proposed future surface:
- `retrieve.py`

### 5. Simulation bridge
Purpose:
- map symbolic operators into model/simulation tags
- connect narrative invariants to formal vocabulary

Proposed future surface:
- `bridge.py`

## Guiding rule

Each module must improve at least one of:
- taxonomy quality
- retrieval quality
- compositional clarity
- routing support
- modeling/simulation bridgeability
- falsifiability of symbolic claims

If a module only makes the system sound smarter, it does not count.

## Recommended build order

1. validation
2. normalization
3. retrieval
4. composition
5. simulation bridge

## Failure conditions

This lane fails if:
- records become inconsistent faster than modules improve them,
- operators cannot be compared or normalized,
- retrieval is too fuzzy to support actual work,
- or the system accumulates symbolic language without operational leverage.
