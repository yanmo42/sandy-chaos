# Contract 5 Receipt — §11 Math Repair + A-006 Ablation

Date: 2026-06-14
Commit: 95e030c

## Option Chosen

OPTION B: keep τ_γ as arc-length integral, remove Cauchy theorem claim.

Rationale: the code (`path_integral`) computes `τ += Z_avg * ds` where
`ds = ‖Δp‖` is always a non-negative scalar. This is definitionally an
arc-length integral `∫ Z(s)|ds|`, not a holomorphic contour integral
`∮ f(z) dz`. Option A would have required rewriting the integration loop
to use `dz = (Δx + i Δy)` as a complex differential — a deeper refactor
not matched by downstream usage. Option B required only removing incorrect
claims and adding correct language.

## What Changed

docs/math_foundations_zf.md §11 (lines ~456–484):
- Removed: "Cauchy's Integral Theorem: ΔT = 0 if Z is holomorphic; ΔT ≠ 0 means singularity enclosed."
- Removed: winding number formula presented as applicable to physical loops.
- Removed: "entropic vortex charge" claim (which depended on Cauchy).
- Added: explicit statement that arc-length differential |ds| ≥ 0 means Cauchy does not apply.
- Added: constraint note — Z = α+iβ with (α,β)∈[0,1]² is always in the first quadrant of ℂ; winding number ≡ 0 identically for all valid inputs.
- Added: correct interpretation — ΔT is a path-integrated entropy summary; ΔT ≠ 0 is the generic case with no topological meaning.

nfem_suite/formalization/complex_euler.py:
- Module docstring: corrected description of path integral and ΔT.
- `temporal_displacement`: removed Cauchy theorem and vortex-charge language; replaced with arc-length integral description.
- `compute_winding_number`: documented the [0,1]² first-quadrant constraint and that output is 0 for all valid inputs.
- Added `path_integral_real()` function: A-006 ablation implementation.

## A-006 Ablation Verdict

The complex embedding buys compact notation only. The path integral
τ = ∫ Z(s)|ds| = ∫ (α+iβ)|ds| is computationally equivalent to two
independent real weighted-path-length sums (τ_re, τ_im). No complex-analysis
theorem (Cauchy, residues, winding) is active or applicable. `path_integral_real()`
confirms numerical identity to 10⁻¹⁰ precision.

## Test Result

338 passed, 6 subtests passed in 1.79s (tests excluding scipy/matplotlib dependency
failures that pre-existed this contract and are unrelated to the changed files).
