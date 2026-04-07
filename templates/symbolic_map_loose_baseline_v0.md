# Symbolic Map Loose Baseline Template v0

**Purpose:** provide the comparison template for **Arm B — loose symbolic-description baseline** in `plans/symbolic_maps_level4_benchmark_v0.md`.

This template is intentionally lighter and less structured than the invariant-guided extraction template.
It is meant to represent a competent, good-faith symbolic reading that does **not** rely on the stronger invariant schema discipline.

The point is not to make Arm B weak.
The point is to make it plausible.

---

## Usage rule

Use one filled copy of this template per artifact.

The operator should:
- produce a coherent symbolic reading in normal interpretive language
- avoid importing the full Arm A schema discipline
- still preserve obvious boundaries and caveats when the source itself insists on them
- avoid deliberately flattening the artifact into mush just to make Arm A look better

Rule:
If Arm B is incompetent, the benchmark is invalid.

---

## Baseline packet

### artifact_id
- `<repo-relative-path-or-short-id>`

### artifact_family
- `symbolic-maps`
- `narrative-invariants`
- `adjacent-symbolic-specimen`
- `<other if needed>`

### baseline_read
Give a short plain-language read of what the artifact seems to be doing.

Keep this to 1 short paragraph.

---

### key_motifs
List the major symbolic or conceptual motifs that stand out.

Format:
- `<motif>` — `<why it seems important>`

Examples:
- `map as navigation` — the artifact wants symbolic work to feel browsable and relational
- `threshold crossing` — the artifact cares about state change through qualitative transition

---

### symbolic_story
Write a short freeform account of the artifact’s symbolic logic.

Suggested length:
- 1–3 paragraphs

This can include:
- what the artifact is trying to name
- what image or tension it is organizing
- what kind of symbolic behavior it seems to privilege

---

### practical_takeaway
What seems most practically useful about the artifact?

Format:
- 2–5 bullets

This should stay informal.
It does not need to be reduced into operator language.

---

### caveats_or_boundaries
What obvious limits or caution notes are present?

Format:
- `<caveat>`

These should be included especially when the source itself warns against overclaiming.

---

### interpretive_tensions
What tensions or ambiguities remain unresolved in the artifact?

Format:
- `<tension>`

Examples:
- wants rigor but still depends on symbolic compression
- gestures toward mechanism without fully cashing it out

---

### likely_reuse
Where does this reading seem likely to help later work?

Format:
- `<reuse area>` — `<why>`

Examples:
- `naming discipline` — keeps the capability legible
- `simulation framing` — suggests a transition worth modeling

---

### baseline_confidence
Choose one:
- `high`
- `medium`
- `low`

Then briefly say why.

This should reflect adequacy of the reading, not depth of affection for the artifact.

---

### likely_loss_from_looseness
What is this looser baseline likely to miss or blur compared with a stronger extraction method?

Format:
- `<likely loss>`

This field is important because Arm B should remain honest about its own limitations.

---

### v0 scoring prep
These are not final benchmark scores, but quick baseline-side notes to support later scoring.

#### predicted_cross_artifact_consistency
- `high | medium | low`
- short why

#### predicted_round_trip_reconstructability
- `high | medium | low`
- short why

#### predicted_completeness
- `high | medium | low`
- short why

#### predicted_downstream_reuse
- `high | medium | low`
- short why

---

## Minimal filled skeleton

```md
### artifact_id
- `docs/symbolic-maps/example.md`

### artifact_family
- `symbolic-maps`

### baseline_read
- This artifact seems to be trying to make symbolic material more usable by giving it a clearer name, role, or transition path into later work.

### key_motifs
- `motif` — `why it matters`

### symbolic_story
This artifact appears to treat symbolic material as something that can be organized rather than merely admired.

### practical_takeaway
- `bullet`

### caveats_or_boundaries
- `caveat`

### interpretive_tensions
- `tension`

### likely_reuse
- `reuse area` — `why`

### baseline_confidence
- `medium` — the source is fairly legible, but this looser reading may blur some distinctions

### likely_loss_from_looseness
- `loss note`

### v0 scoring prep
#### predicted_cross_artifact_consistency
- `medium` — enough overlap may survive, but naming could drift between artifacts

#### predicted_round_trip_reconstructability
- `medium` — the main gist is likely recoverable, but some structure may be lost

#### predicted_completeness
- `medium` — the baseline can cover the main themes without capturing all boundaries

#### predicted_downstream_reuse
- `medium` — useful for orientation, less reliable for validation or comparison`
```

---

## Design note

Arm B is supposed to feel like a smart human symbolic reading done without the stronger invariant apparatus.

That means it should still be:
- honest
- readable
- interpretively competent
- aware of the source’s own cautions

But it should not automatically produce:
- stable operator vocabulary
- clean role schemas
- explicit invariant candidates
- strong mechanism/metaphor separation
- reusable structural packets

If it does all of that naturally, then Arm A may not actually be buying much.

---

## Immediate next action

Use this template to create the first loose baseline reading for:
- `docs/symbolic-maps/symbolic_operator_extraction_naming.md`
