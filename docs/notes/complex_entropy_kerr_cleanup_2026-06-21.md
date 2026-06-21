# Cleanup Receipt — Complex-Entropy & Kerr (2026-06-21)

Step 5 (non-gating) of `plans/defensible-frontier-2026-06-21.md`. Records the disposition
of the two parallel-hygiene items so neither silently re-enters load-bearing prose.

## 1) Complex-entropy formalism `Z = α + iβ` — RETIRE as load-bearing, keep as notation

The §11 fix (earlier C5 work) already corrected `nfem_suite/formalization/complex_euler.py`
(arc-length ≠ holomorphic contour integral; winding returns 0 for valid inputs) and shipped
an ablation `path_integral_real`. This step **verifies** that ablation numerically:

- **Exact equivalence.** On a 200-point random path, the complex integral
  `τ = ∫ Z|ds|` and the plain real pair `(τ_re, τ_im) = (∫α|ds|, ∫β|ds|)` agree to
  **max abs difference 0.00e+00**. The ℂ embedding adds nothing the two real integrals
  don't already carry.
- **Constrained case is 1-D.** Under the model's bijection `β = 1 − α`, the state
  `Z = α + i(1−α)` traces a line segment; `(|Z|, φ)` is a bijection of `α` alone — there
  is no genuine two-dimensional complex phase space to exploit.
- **No topological content.** For valid `(α,β) ∈ [0,1]²` (first quadrant), the winding
  number around the origin is `3.5e-17 ≈ 0`. No Cauchy/residue/vortex-charge diagnostic
  is available, as the corrected docstrings already state.

**Verdict:** the complex embedding is **decorative** for every current use — convenient
notation (`|Z|`, `φ`) but not a source of theoretical leverage. It is **retired as
load-bearing**: no claim may invoke complex-analysis theorems (Cauchy, residues, winding)
over this object unless and until a genuine holomorphic contour integral with an enclosed
singularity is constructed — which the confined `[0,1]²` data cannot currently support.
Nothing downstream is lost by reading results in plain `(order, disorder) ∈ ℝ²`.

## 2) Kerr / rotating-spacetime layer — confirmed ILLUSTRATIVE-ONLY

`docs/theory-implementation-matrix.md` row T-015 is **REVIEW / Low confidence**, carrying
the 2026-06-10 audit caveat (the benchmark measured affine-parameter step counts on null
geodesics, not proper time; non-discriminating flat comparator). The retraction-pending
annotation is in `docs/math_foundations_zf.md` §9 and `plans/todo.md`. The Kerr layer is
**not load-bearing** anywhere downstream; it stands as illustrative geometry only. No
action needed beyond keeping it out of evidence-bearing claims until a rebuild with an
invariant observable + Sagnac baseline is run.

## Net

Both hygiene items are dispositioned: complex-entropy retired as load-bearing (verified
equivalent to ℝ²), Kerr confirmed illustrative-only. Neither blocks the defensible
frontier (retrodiction + moving-observer + self-consistency), all of which avoid both.
