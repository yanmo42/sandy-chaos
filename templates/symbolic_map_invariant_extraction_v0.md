# Symbolic Map Invariant Extraction Template v0

**Purpose:** provide the constrained extraction template for **Arm A — invariant-guided extraction** in `plans/symbolic_maps_level4_benchmark_v0.md`.

This template is intentionally small.
It should capture enough structure to support comparison, reconstruction, and reuse without turning the benchmark into schema theater.

---

## Usage rule

Use one filled copy of this template per artifact.

The operator should:
- preserve distinctions between **symbol**, **model translation**, and **mechanism claims**
- prefer concise structural entries over long interpretive paragraphs
- record uncertainty explicitly rather than smoothing it away
- avoid inventing invariants that the artifact does not support

If a field cannot be filled honestly, say so.
Sparse truth is better than decorative completion.

---

## Extraction packet

### artifact_id
- `<repo-relative-path-or-short-id>`

### artifact_family
- `symbolic-maps`
- `narrative-invariants`
- `adjacent-symbolic-specimen`
- `<other if needed>`

### artifact_role
Short phrase for what kind of artifact this is.

Examples:
- `module-roadmap`
- `naming-contract`
- `symbolic-specimen-translation`
- `operator-schema-note`

### source_mode
How the source primarily behaves.

Choose one primary mode:
- `architecture`
- `schema-contract`
- `specimen-translation`
- `interpretive-note`
- `bridge-note`

### core_question
What question is this artifact implicitly trying to answer?

Keep to 1–2 sentences.

---

## symbolic_entities
List the main symbolic entities or objects that carry structure in the artifact.

Format:
- `<entity>` — `<short role>`

Examples:
- `Rimuru-like figure` — compressed intuition carrier for adaptive-substrate transition
- `Symbolic Map` — human-facing artifact family
- `Narrative Invariant Extractor` — internal technical mechanism label

---

## roles
List the stable roles that matter across interpretation.

Format:
- `<role>` — `<who/what occupies it here>`

Examples:
- `substrate` — minimally committed adaptive medium
- `organizer` — post-transition coherence-shaping role
- `extractor` — mechanism that derives reusable operators from narrative material

---

## relations
List the key relations between entities/roles.

Format:
- `<source> -> <relation> -> <target>`

Examples:
- `extractor -> emits -> symbolic maps`
- `adaptive substrate -> crosses -> snap threshold`
- `symbolic specimen -> maps into -> neutral model vocabulary`

Prefer 3–8 relations.

---

## operators_or_transformations
What reusable operations or transformations are implied?

Format:
- `<operator name>` — `<what it does>`

Examples:
- `extract_invariants` — compress narrative object into reusable structural roles
- `normalize_operators` — convert symbolic variance into comparable operator labels
- `threshold_transition` — shift a system into a new behavioral regime after crossing a snap point

This field matters a lot for later reuse.

---

## candidate_invariants
List the strongest invariant candidates preserved across the artifact.

Format:
- `<candidate invariant>` — `<why it looks stable here>`

Examples:
- `symbolic role can be translated into neutral model language` — artifact explicitly pairs symbolic and formal vocabulary
- `operator extraction must preserve failure modes` — repeated as a boundary condition, not just a style choice

Rule:
A candidate invariant should be more stable than a one-off motif.
If it is merely a theme, do not call it an invariant.

---

## constraints_or_boundaries
What explicit constraints keep the artifact from overclaiming?

Format:
- `<constraint>`

Examples:
- metaphor is not evidence of mechanism
- symbolic prose without operational leverage does not count
- schema inflation is not validation

This field is critical for distinguishing disciplined structure from vibes.

---

## failure_conditions
What would materially weaken or falsify the artifact's usefulness in the symbolic-maps family?

Format:
- `<failure condition>`

Examples:
- extraction produces elegance without comparison leverage
- model translation cannot be operationalized
- invariant candidates collapse under cross-artifact comparison

Prefer artifact-specific failure conditions over generic ones.

---

## reuse_candidates
What downstream uses does this extraction appear to support?

Format:
- `<reuse target>` — `<why>`

Examples:
- `validator design` — extracted constraints can become schema checks
- `operator comparison` — repeated operators can be compared across artifacts
- `naming discipline` — stable distinctions between mechanism/artifact/presentation can be preserved

---

## claim_tier_posture
What is the claim posture of the artifact as extracted?

Use any combination that applies:
- `defensible-now`
- `plausible-but-unproven`
- `speculative`

Then add 1–3 bullets describing where the extracted structure sits.

This field exists to preserve epistemic hygiene during extraction.

---

## mechanism_vs_metaphor_split
Separate what appears to be:

### mechanism-bearing
- `<items that cash out into operational structure>`

### metaphor-bearing
- `<items that orient thinking but do not yet prove mechanism>`

### unresolved
- `<items that might become mechanism later but are not there yet>`

This field is especially important for specimen-style artifacts.

---

## round_trip_reconstruction_note
In 3–6 bullets, write what another operator would need in order to reconstruct the core logic of the artifact from this extraction alone.

If you cannot do this cleanly, the extraction is probably too weak.

---

## extraction_confidence
Choose one:
- `high`
- `medium`
- `low`

Then briefly say why.

Confidence should reflect extraction adequacy, not affection for the artifact.

---

## ambiguity_or_loss_notes
Record anything important that may have been lost, blurred, or forced by the extraction.

Format:
- `<ambiguity or loss>`

This field helps prevent false confidence from rigid templates.

---

## v0 scoring prep
These are not final benchmark scores, but quick extractor-side notes to support later scoring.

### predicted_cross_artifact_consistency
- `high | medium | low`
- short why

### predicted_round_trip_reconstructability
- `high | medium | low`
- short why

### predicted_schema_completeness
- `high | medium | low`
- short why

### predicted_downstream_reuse
- `high | medium | low`
- short why

---

## Minimal filled skeleton

```md
### artifact_id
- `docs/symbolic-maps/example.md`

### artifact_family
- `symbolic-maps`

### artifact_role
- `symbolic-specimen-translation`

### source_mode
- `specimen-translation`

### core_question
- How can a culturally legible symbolic figure be translated into neutral model language without collapsing metaphor into mechanism?

### symbolic_entities
- `example entity` — `short role`

### roles
- `role name` — `occupant`

### relations
- `A -> relation -> B`

### operators_or_transformations
- `operator_name` — `what it does`

### candidate_invariants
- `candidate invariant` — `why it appears stable`

### constraints_or_boundaries
- `constraint`

### failure_conditions
- `failure condition`

### reuse_candidates
- `reuse target` — `why`

### claim_tier_posture
- `plausible-but-unproven`
- structure appears reusable, but benchmark discrimination is still missing

### mechanism_vs_metaphor_split
#### mechanism-bearing
- `item`

#### metaphor-bearing
- `item`

#### unresolved
- `item`

### round_trip_reconstruction_note
- `bullet`

### extraction_confidence
- `medium` — extraction preserves main structure but some semantic compression may hide nuance

### ambiguity_or_loss_notes
- `note`

### v0 scoring prep
#### predicted_cross_artifact_consistency
- `medium` — likely overlap with naming/roadmap artifacts but not yet proven

#### predicted_round_trip_reconstructability
- `high` — core logic appears structurally recoverable

#### predicted_schema_completeness
- `medium` — some fields may remain sparse depending on artifact type

#### predicted_downstream_reuse
- `medium` — useful for comparison and later validator design if repeated patterns survive`
```

---

## Immediate next action

Use this template to fill the first extraction packet for:
- `docs/symbolic-maps/symbolic_maps_intelligence_modules.md`
- `docs/symbolic-maps/symbolic_operator_extraction_naming.md`
- `docs/symbolic-maps/rimuru_adaptive_substrate_snap_model.md`
