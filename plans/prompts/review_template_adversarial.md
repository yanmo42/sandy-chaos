# Adversarial Review Template

Use this after a prompt packet produces code, tests, docs, or evidence.

The point is not politeness.
The point is to discover whether the work actually survives pressure.

---

## Review header

- **prompt_id:**
- **artifact(s) reviewed:**
- **reviewer:**
- **date:**
- **overall disposition:** ACCEPT | REVISE | REJECT | NEEDS MORE EVIDENCE

---

## 1) What was the work trying to do?

State the packet objective in one or two sentences.
If the objective is fuzzy here, the packet or implementation is already in trouble.

---

## 2) What seems genuinely solid?

List the parts that appear real, bounded, and inspectable.

Prefer concrete statements such as:
- interface exists at path X,
- baseline comparison is real,
- failure mode Y is handled,
- provenance is visible in artifact Z.

---

## 3) Where is the fake rigor?

Look for:
- impressive terminology masking a weak interface,
- benchmarks without a real comparator,
- hand-wavy architecture language,
- diagrammatic confidence unsupported by code or tests,
- proofs-by-vibe.

---

## 4) Which invariants were preserved, and which were violated?

Check especially:
- claim-tier discipline,
- authority boundaries,
- provenance visibility,
- fallback behavior,
- interface legibility,
- bounded scope.

---

## 5) What collapsed that should have stayed distinct?

Examples:
- symbolic -> operational
- experimental -> canonical
- planning -> governance
- utility -> authority
- archive -> present legitimacy

If nothing collapsed, say so explicitly.

---

## 6) What hidden assumptions is the implementation leaning on?

List assumptions that were not made explicit in the packet or outputs.

These often include:
- environment assumptions,
- manual operator knowledge,
- undocumented file conventions,
- benchmark cherry-picking,
- unstated interpretation rules.

---

## 7) What evidence is still missing?

Be concrete.

Examples:
- needs a flat baseline,
- needs regression coverage,
- needs a live consumer,
- needs failure traces,
- needs clearer provenance output,
- needs a declared membrane before this can affect other layers.

---

## 8) Defensible / Plausible / Speculative residue

### Defensible now
What can actually be said after this work?

### Plausible but unproven
What looks promising but is not yet earned?

### Speculative
What should remain fenced off despite temptation to promote it?

---

## 9) Most likely failure mode if we accept this too early

State the concrete architectural or epistemic risk.

---

## 10) Required revisions

List the smallest set of revisions needed to turn this into something acceptable.

If rejection is the right call, say why cleanly.

---

## 11) Final verdict

One paragraph max.

Format suggestion:

- what survives,
- what fails,
- whether another iteration is justified,
- what next packet should target.
