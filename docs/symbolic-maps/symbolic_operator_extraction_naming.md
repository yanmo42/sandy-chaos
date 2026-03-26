# Symbolic Operator Extraction - Naming Note

## Purpose

Capture the naming decision for the capability we have been circling:
extracting reusable functional structure from culturally legible characters, symbols, stories, and media objects.

## Recommended naming split

### Internal technical name
**Narrative Invariant Extractor**

Why:
- emphasizes structure rather than vibes,
- points toward cross-domain invariants,
- keeps the framing usable in research/spec contexts.

### Capability class
**Symbolic Operator Extraction**

Why:
- says what the system actually does,
- keeps symbol and function explicitly joined,
- supports downstream composition language.

### Human-facing artifact family
**Symbolic Maps**

Why:
- easy to say,
- easy to browse,
- suggests relational navigation rather than ontology claims,
- scales to character maps, media maps, operator maps, and analogy maps.

## Functional definition

The system should:
1. ingest narrative/media objects,
2. identify compressed symbolic roles,
3. extract reusable functional operators,
4. preserve failure modes and exclusions,
5. and compose outputs into navigable maps or downstream action frames.

## Suggested architecture language

Pipeline:
- ingest
- parse
- extract invariants
- normalize to operators
- annotate constraints / failure modes
- emit symbolic maps

## Example naming stack

- module: `narrative_invariants`
- package: `symbolic_maps`
- schema: `symbolic_operator.schema.json`
- record type: `SymbolicOperatorRecord`
- pipeline stage: `extract_symbolic_operators`
- artifact: `gojo.symbolic-map.json`

## Record skeleton

Suggested fields:
- `source_object`
- `source_domain`
- `narrative_role`
- `core_fantasy`
- `signature_operators`
- `constraint_pattern`
- `failure_modes`
- `composable_with`
- `excluded_domains`
- `confidence_tier`
- `notes`

## Boundary note

This capability is only useful if extraction improves:
- taxonomy,
- prediction,
- design language,
- agent routing,
- simulation priors,
- or interface compression.

If it only generates elegant symbolic prose, it has not yet completed the loop into functional AI.

## Recommended working phrasing

Use this phrasing going forward:

> We are building a Narrative Invariant Extractor that performs Symbolic Operator Extraction and emits Symbolic Maps.

That gives us:
- rigor internally,
- usability externally,
- and clean separation between mechanism, artifact, and presentation.
