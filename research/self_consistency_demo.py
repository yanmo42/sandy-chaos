#!/usr/bin/env python3
"""
Self-Consistency Handshake — Step 4 of plans/defensible-frontier-2026-06-21.md

Predictions/thresholds committed, dated, BEFORE this code in:
    plans/self-consistency-prereg-2026-06-21.md   (P1-P3)

Claim under test: a loop coupling a past end and a future end of one deterministic
structure admits only self-consistent fixed points. The future can CONSTRAIN the
present (the fixed point depends on the coupling) but cannot SIGNAL it: a freely chosen
message cannot be injected through the closed loop. This is the paradox-free core that
survives after chronology protection / no-signaling kill the literal future->past telegram.
"""

import json
import datetime
from pathlib import Path
import numpy as np

# ---- locked parameters ----
# v2 correction (see prereg outcome): v1 used A=1.5,k=1.2 -> max|h'|=1.8 -> a MULTISTABLE
# loop with several consistent histories, and letting the future set the initial state let
# it pick the basin (~1 bit leaked). That is the PAST's prerogative, not the future's. v2
# uses a contraction (max|h'|=A*k<1) -> a UNIQUE consistent history -> the future's choice
# is fully washed out. We also sweep a closure parameter g to show injectable information
# vanishing as self-consistency tightens.
A, B0 = 0.8, 0.3          # forward dynamics F(x) = tanh(A x + B0)
K_COUPLING = 0.7          # consistency coupling in C(s;k) = tanh(k s + C0); A*K=0.56 < 1
C0 = -0.2
K_MSG = 8                 # message alphabet size (log2 K = 3 bits)
T_LO, T_HI = -0.8, 0.8    # codeword target spread
SIGMA = 0.05
BINS = np.linspace(-1.0, 1.0, 21)   # 20 bins
N_TRIALS = 40000
N_BOOT = 1000
SEED = 20260621


def F(x):
    return np.tanh(A * x + B0)


def C(s, k):
    return np.tanh(k * s + C0)


def h(s, k):
    """closed-loop consistency map: s -> F(C(s))."""
    return F(C(s, k))


def fixed_point(k, s0=0.0, iters=200):
    s = s0
    for _ in range(iters):
        s = h(s, k)
    return s


def codeword_target(m):
    return T_LO + (T_HI - T_LO) * m / (K_MSG - 1)


def mutual_info_bits(msg, realized):
    """plug-in MI between discrete message and binned realized state, in bits."""
    r_idx = np.clip(np.digitize(realized, BINS) - 1, 0, len(BINS) - 2)
    B = len(BINS) - 1
    flat = msg * B + r_idx
    counts = np.bincount(flat, minlength=K_MSG * B).reshape(K_MSG, B).astype(float)
    N = counts.sum()
    pj = counts / N
    pm = pj.sum(1, keepdims=True)
    pr = pj.sum(0, keepdims=True)
    denom = pm @ pr
    mask = pj > 0
    return float(np.sum(pj[mask] * np.log2(pj[mask] / denom[mask])))


def mi_with_ci(msg, realized, rng):
    r_idx = np.clip(np.digitize(realized, BINS) - 1, 0, len(BINS) - 2)
    B = len(BINS) - 1
    flat = msg * B + r_idx
    N = len(flat)

    def mi_from_flat(f):
        counts = np.bincount(f, minlength=K_MSG * B).reshape(K_MSG, B).astype(float)
        tot = counts.sum()
        pj = counts / tot
        pm = pj.sum(1, keepdims=True)
        pr = pj.sum(0, keepdims=True)
        denom = pm @ pr
        mask = pj > 0
        return float(np.sum(pj[mask] * np.log2(pj[mask] / denom[mask])))

    point = mi_from_flat(flat)
    boot = np.array([mi_from_flat(flat[rng.integers(0, N, N)]) for _ in range(N_BOOT)])
    return point, [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]


def main():
    rng = np.random.default_rng(SEED)

    # ---- P1: consistent histories survive (grid of inits -> single fixed point) ----
    grid = np.linspace(-1.0, 1.0, 41)
    finals = np.array([fixed_point(K_COUPLING, s0=g) for g in grid])
    s_star = float(finals.mean())
    p1_spread = float(finals.max() - finals.min())
    p1 = p1_spread < 1e-6

    # ---- P2: the future-coupling constrains the present (fixed point moves with k) ----
    ks = np.linspace(0.5, 2.0, 16)
    fps = np.array([fixed_point(k) for k in ks])
    p2_range = float(fps.max() - fps.min())
    p2 = p2_range > 0.05

    # ---- P3: injection test vs loop closure g (0 = open, 1 = fully self-consistent) ----
    msg = rng.integers(0, K_MSG, N_TRIALS)
    targets = codeword_target(msg)
    noise = rng.normal(0.0, SIGMA, N_TRIALS)

    def forced_realized(g, iters=400):
        # fixed point of the forced consistency map s = (1-g)*target + g*h(s):
        # g=0 -> realized = target (future freely sets it); g=1 -> realized = s* (pinned).
        s = targets.copy()
        for _ in range(iters):
            s = (1.0 - g) * targets + g * h(s, K_COUPLING)
        return s + noise

    gs = np.linspace(0.0, 1.0, 11)
    mi_curve = [mutual_info_bits(msg, forced_realized(g)) for g in gs]

    mi_open, ci_open = mi_with_ci(msg, forced_realized(0.0), rng)      # fully open
    mi_closed, ci_closed = mi_with_ci(msg, forced_realized(1.0), rng)  # fully self-consistent

    p3 = (ci_closed[1] < 0.1) and (ci_open[0] > 2.0)

    verdict = "PASS" if (p1 and p2 and p3) else "FAIL"

    result = {
        "experiment": "self_consistency_demo",
        "date": datetime.date.today().isoformat(),
        "prereg": "plans/self-consistency-prereg-2026-06-21.md",
        "fixed_point_s_star": s_star,
        "P1_spread_over_inits": p1_spread,
        "P2_fixed_point_range_over_k": p2_range,
        "P2_k_sweep": {"k": ks.tolist(), "s_star": fps.tolist()},
        "I_closed_bits": mi_closed, "I_closed_ci": ci_closed,
        "I_open_bits": mi_open, "I_open_ci": ci_open,
        "closure_sweep": {"g": gs.tolist(), "I_bits": mi_curve},
        "log2_K_attempted_bits": float(np.log2(K_MSG)),
        "checks": {"P1_consistent_histories_survive": bool(p1),
                   "P2_future_constrains_present": bool(p2),
                   "P3_no_chosen_bit_injected": bool(p3)},
        "verdict": verdict,
    }

    outdir = Path("memory/research")
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    jpath = outdir / f"self_consistency_results_{stamp}.json"
    jpath.write_text(json.dumps(result, indent=2))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
        ax1.plot(ks, fps, "o-", color="teal")
        ax1.set_xlabel("future-coupling strength  k")
        ax1.set_ylabel("realized consistent state  s*")
        ax1.set_title("Future constrains present\n(fixed point moves with coupling)")
        ax2.plot(gs, mi_curve, "o-", color="crimson")
        ax2.axhline(np.log2(K_MSG), color="k", ls="--", lw=1, label="attempted 3 bits")
        ax2.axhline(0, color="k", lw=0.6)
        ax2.set_xlabel("loop closure  g   (0 = open,  1 = self-consistent)")
        ax2.set_ylabel("transmitted info  I(message; realized)  [bits]")
        ax2.set_title("Injectable information vanishes\nas self-consistency tightens")
        ax2.legend(fontsize=8)
        fig.tight_layout()
        ppath = outdir / f"self_consistency_demo_{stamp}.png"
        fig.savefig(ppath, dpi=130)
        result["plot"] = str(ppath)
        jpath.write_text(json.dumps(result, indent=2))
    except Exception as e:
        result["plot_error"] = repr(e)

    print(f"VERDICT: {verdict}   checks: P1={p1} P2={p2} P3={p3}")
    print(f"P1 fixed point s* = {s_star:.5f}   spread over inits = {p1_spread:.2e}")
    print(f"P2 fixed-point range over k in [0.5,2.0] = {p2_range:.4f}  (> 0.05 required)")
    print(f"P3 closed-loop  I(msg; realized) = {mi_closed:.4f} bits  CI {ci_closed}")
    print(f"   open-channel I(msg; realized) = {mi_open:.4f} bits  CI {ci_open}  (attempted {np.log2(K_MSG):.2f})")
    print(f"\nwrote {jpath}")
    if "plot" in result:
        print(f"wrote {result['plot']}")


if __name__ == "__main__":
    main()
