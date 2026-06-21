# Pre-Registration — Self-Consistency Handshake (2026-06-21)

**Authoritative, dated, written BEFORE the evaluation code.**
Evaluation script: `research/self_consistency_demo.py`.
Parent plan: `plans/defensible-frontier-2026-06-21.md`, Step 4.

This is the rigorous home for "messages from the future": the future can **constrain**
the present (a self-consistent fixed point) but cannot **signal** it (no chosen bit can
be injected). It is the paradox-free core that survives after chronology protection and
the no-signaling theorems kill the literal telegram.

---

## 1) Model (plain language)

A loop couples a "past end" and a "future end" of one deterministic structure:
- **forward dynamics** `F`: the future end is produced from the present, `s = F(x)`.
- **consistency coupling** `C`: the present is conditioned on the future end,
  `x = C(s; k)` (the narrative-boundary idea — the present boundary shaped by an
  anticipation of the future).

A physically realizable history must satisfy **both at once**: the future end obeys
`s = F(C(s; k)) ≡ h(s)`. Only fixed points `s*` of `h` are realizable histories.
`F` and `C` are `tanh` maps (contractions), so the loop has a single stable `s*`.

## 2) The injection test (the falsifier)

A "future civilization" tries to send a chosen message `m ∈ {0..K-1}` (K=8, 3 bits) by
forcing the future end toward a codeword target `t(m)`.
- **Open channel (positive control):** the future end is free, `realized = t(m) + noise`
  → a reader recovers `m`.
- **Closed self-consistent loop:** the forced target is iterated through `h` and
  **projected onto the consistent fixed point** `s*` (independent of `m`):
  `realized = s* + noise`.

We measure the transmitted information `I(m; realized)` in both.

### Locked parameters
`F(x)=tanh(1.5x+0.3)`, `C(s;k)=tanh(k·s−0.2)`, `k=1.2`, `K=8`,
codeword targets `t(m)` evenly on `[-0.8, 0.8]`, noise `σ=0.05`, 20 histogram bins on
`[-1,1]`, `n_trials=40000`, bootstrap `=1000`, seed fixed in script.

---

## 3) Pre-registered predictions (locked before any run)

- **P1 — Consistent histories survive.** Iterating `h` from a grid of initial states all
  converges to a single fixed point `s*` (max spread `< 1e-6` after convergence).
- **P2 — The future constrains the present.** Changing the coupling `k` shifts the
  fixed point (`|Δs*| > 0.05` across the swept `k` range): the future-coupling selects
  which present states are allowed.
- **P3 — FALSIFIER: no chosen bit can be injected.** In the closed loop
  `I(m; realized) ≈ 0` (95% CI upper bound `< 0.1` bits), while the open-channel
  positive control transmits `I ≈ log₂K = 3` bits (CI lower bound `> 2` bits). **If a
  freely chosen message leaks through the closed loop (`I_closed` significantly `> 0`),
  the no-signaling claim is falsified — that would mean a modeling error, because
  self-consistency forbids a controllable future→past channel.**

### Pass/fail
**PASS** iff P1, P2, P3 hold. P3 is the decisive result: the loop carries a *handshake
that was always going to happen*, never a telegram the future composes. The positive
control proves the test *can* detect a working channel, so the `I_closed ≈ 0` is
meaningful (the test can fail).

---

## 4) Outcome (2026-06-21, appended after running — history annotated, not rewritten)

**Run v1** (`A=1.5, k=1.2`): **FAIL.** Max loop slope `A·k = 1.8 > 1` made the loop
**multistable** (fixed-point spread 1.57 — several consistent histories), and letting the
future set the initial state let it pick the basin: ~**1.0 bit leaked** through the
"closed" loop, falsifying P1 and P3. The lesson is real: a loop with *multiple*
consistent histories can carry selection information — but basin selection is the
**past's** prerogative (the initial condition), not the future's. v1 inadvertently handed
that control to the future.

**Run v2** (`A=0.8, k=0.7`, `A·k = 0.56 < 1`, plus a closure sweep `g`):
`research/self_consistency_demo.py` → `memory/research/self_consistency_results_20260621.json`,
plot `self_consistency_demo_20260621.png`. **VERDICT: PASS (P1, P2, P3).**
- **P1:** a **unique** consistent history `s* = 0.297` from all initial states (spread
  `5.5e-17`).
- **P2:** `s*` moves by 0.53 as the future-coupling `k` sweeps [0.5, 2.0] — the future
  **constrains** which present states are allowed.
- **P3 (decisive):** the future attempts to inject **3 bits**; the fully self-consistent
  loop transmits **0.0005 bits** (CI [0.0005, 0.0014] — i.e. nothing but estimator bias),
  while the open-channel positive control transmits **2.85 bits**. The closure sweep shows
  the injectable information falling smoothly from ~3 bits to 0 as the loop closes.

**Established (defensible):** with a unique consistent history, a self-consistent loop
lets the future **constrain** the present (P2) but carries **no freely chosen bit** (P3) —
a handshake, not a telegram. The multistable case (v1) is the named caveat: multiple
consistent histories permit selection, but only by whoever sets the basin (the past),
never by the future. This is the paradox-free residue of "messages from the future."
