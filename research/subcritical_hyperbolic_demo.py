#!/usr/bin/env python3
"""
Pre-registered Predictions (AUD-003 / T-002)
============================================
1. In the 1D linearized shallow-water hyperbolic system, a downstream perturbation
   at x=L propagates upstream at the finite characteristic wave speed c_up = sqrt(gH) - u.
2. The measured onset delay tau_measured at x_obs < L will match the theoretical delay
   tau_theoretical = (L - x_obs) / c_up within 10%.
3. In contrast, the parabolic baseline (advection-diffusion or pure diffusion) propagates
   information at infinite speed, leading to instantaneous "leakage" at x_obs. Reducing
   the detection threshold will make the parabolic onset delay approach zero, whereas
   the hyperbolic onset delay will remain bounded and robust near tau_theoretical.
4. The mutual information I(q(x_obs, t); B) for the hyperbolic system will remain strictly
   zero (noise-floor limited) until t = t_switch + tau_theoretical, after which it will rise.
5. The regime transition sweep of mutual information against Froude number Fr = u/sqrt(gH)
   will show that as Fr approaches 1 (critical flow), c_up approaches 0, causing the delay
   to approach infinity, which suppresses mutual information within any finite observation window.
"""

import os
import json
import datetime
from pathlib import Path
import numpy as np

# Try to import matplotlib for plotting
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ============================================================
# 1. Analytical Mutual Information
# ============================================================

def gaussian_binary_mi(signal_strength, noise_std, n_quad=4000):
    """
    Exact mutual information I(Q; B) for a binary symmetric channel
    with additive Gaussian noise.
    
    B in {0, 1} equally likely. Q = B * signal_strength + N(0, sigma^2).
    """
    s = abs(float(signal_strength))
    sigma = float(noise_std)
    if sigma <= 0:
        return 1.0 if s > 0 else 0.0
    if s < 1e-15:
        return 0.0

    # Conditional entropy H(Q|B) = 0.5 * log2(2 * pi * e * sigma^2)
    h_cond = 0.5 * np.log2(2.0 * np.pi * np.e * sigma ** 2)

    # Numerical quadrature to find the mixture entropy H(Q)
    lo = min(0.0, s) - 7.0 * sigma
    hi = max(0.0, s) + 7.0 * sigma
    q_grid = np.linspace(lo, hi, n_quad)
    dq = q_grid[1] - q_grid[0]

    # Mixture density p(q) = 0.5 * N(0, sigma^2) + 0.5 * N(s, sigma^2)
    log_p0 = -0.5 * (q_grid / sigma) ** 2
    log_p1 = -0.5 * ((q_grid - s) / sigma) ** 2
    log_max = np.maximum(log_p0, log_p1)
    log_mix = log_max + np.log(np.exp(log_p0 - log_max) + np.exp(log_p1 - log_max))
    log_norm = -np.log(2.0 * sigma * np.sqrt(2.0 * np.pi))
    log_p = log_norm + log_mix

    p = np.exp(log_p)
    mask = p > 1e-300
    h_q = -np.sum(p[mask] * log_p[mask] * dq) / np.log(2.0)

    mi = h_q - h_cond
    return float(max(mi, 0.0))


# ============================================================
# 2. Tridiagonal System Solver (Thomas Algorithm)
# ============================================================

def thomas_solve(a, b, c, d):
    """Thomas algorithm for tridiagonal system Ax = d."""
    n = len(d)
    c_prime = np.zeros(n)
    d_prime = np.zeros(n)
    
    c_prime[0] = c[0] / b[0]
    d_prime[0] = d[0] / b[0]
    
    for i in range(1, n):
        denom = b[i] - a[i-1] * c_prime[i-1]
        if i < n - 1:
            c_prime[i] = c[i] / denom
        d_prime[i] = (d[i] - a[i-1] * d_prime[i-1]) / denom
        
    x = np.zeros(n)
    x[-1] = d_prime[-1]
    for i in range(n-2, -1, -1):
        x[i] = d_prime[i] - c_prime[i] * x[i+1]
    return x


# ============================================================
# 3. 1D Linearized Shallow-Water Hyperbolic Solver
# ============================================================

def solve_hyperbolic_shallow_water(u, g, H, L, nx, dt, n_steps, bc_right_fn):
    """
    Solves the 1D linearized shallow water equations on [0, L]
    by transforming to decoupled Riemann invariants:
      w1_t + l1 * w1_x = 0  (l1 = u + c0 > 0)
      w2_t + l2 * w2_x = 0  (l2 = u - c0 < 0)
      
    with boundary conditions:
      w1(0, t) = 0
      eta(L, t) = (w1(L, t) - w2(L, t)) / (2 * sqrt(g/H)) = B(t)
      => w2(L, t) = w1(L, t) - 2 * sqrt(g/H) * B(t)
    """
    c0 = np.sqrt(g * H)
    l1 = u + c0
    l2 = u - c0
    dx = L / (nx - 1)
    x = np.linspace(0, L, nx)
    
    w1 = np.zeros(nx)
    w2 = np.zeros(nx)
    
    eta_history = []
    times = []
    
    for n in range(n_steps):
        t_n = n * dt
        times.append(t_n)
        
        # Reconstruct physical state
        factor = 2.0 * np.sqrt(g / H)
        eta = (w1 - w2) / factor
        eta_history.append(eta.copy())
        
        w1_next = np.zeros(nx)
        w2_next = np.zeros(nx)
        
        # Upwind scheme for w1 (l1 > 0, info travels from left to right)
        w1_next[1:] = w1[1:] - (l1 * dt / dx) * (w1[1:] - w1[:-1])
        w1_next[0] = 0.0
        
        # Upwind scheme for w2 (l2 < 0, info travels from right to left)
        w2_next[:-1] = w2[:-1] - (l2 * dt / dx) * (w2[1:] - w2[:-1])
        
        # Boundary condition at x=L
        B_np1 = bc_right_fn(t_n + dt)
        w2_next[-1] = w1_next[-1] - factor * B_np1
        
        w1 = w1_next
        w2 = w2_next
        
    times = np.array(times)
    eta_history = np.array(eta_history)
    return x, times, eta_history


# ============================================================
# 4. Parabolic Pure-Diffusion Solver
# ============================================================

def solve_parabolic_diffusion(D, L, nx, dt, n_steps, bc_right_fn):
    """
    Solves dq/dt = D * d^2q/dx^2 on [0, L]
    using Crank-Nicolson with boundary conditions:
      q(0, t) = 0
      q(L, t) = B(t)
    """
    dx = L / (nx - 1)
    x = np.linspace(0, L, nx)
    alpha = D * dt / (2.0 * dx ** 2)
    
    q = np.zeros(nx)
    q_history = []
    times = []
    
    for n in range(n_steps):
        t_n = n * dt
        times.append(t_n)
        q_history.append(q.copy())
        
        # Build Crank-Nicolson tridiagonal system for interior nodes
        n_int = nx - 2
        a = np.full(n_int - 1, -alpha)
        b = np.full(n_int, 1.0 + 2.0 * alpha)
        c = np.full(n_int - 1, -alpha)
        
        rhs = np.zeros(n_int)
        for j in range(1, nx-1):
            idx = j - 1
            rhs[idx] = alpha * q[j-1] + (1.0 - 2.0 * alpha) * q[j] + alpha * q[j+1]
            
        # Add boundary conditions
        B_np1 = bc_right_fn(t_n + dt)
        rhs[0] += alpha * 0.0
        rhs[-1] += alpha * B_np1
        
        q_next = np.zeros(nx)
        q_next[1:-1] = thomas_solve(a, b, c, rhs)
        q_next[0] = 0.0
        q_next[-1] = B_np1
        
        q = q_next
        
    times = np.array(times)
    q_history = np.array(q_history)
    return x, times, q_history


# ============================================================
# 5. Main Analysis and Execution
# ============================================================

def main():
    print("SANDY CHAOS — CONTRACT 3: Hyperbolic Subcritical Mechanism (AUD-003)")
    
    # 1. Define physical constants and grid
    g = 9.81
    H = 1.0
    L = 10.0
    nx = 501
    dx = L / (nx - 1)
    x = np.linspace(0, L, nx)
    
    obs_idx = 100  # x_obs = 2.0 exactly
    x_obs = x[obs_idx]
    
    # CFL-safe dt for max wave speed at Fr=0.95
    c0 = np.sqrt(g * H)
    l1_max = 1.95 * c0  # l1 = u + c0 = (Fr+1)*c0
    dt = 0.9 * dx / l1_max  # dt around 0.003
    n_steps = int(6.0 / dt)
    
    print(f"Grid nx={nx}, dx={dx:.4f}, x_obs={x_obs:.1f}")
    print(f"Time steps={n_steps}, dt={dt:.5f}, total time={n_steps*dt:.2f}s")
    
    # Boundary step perturbation at t=1.0s
    t_switch = 1.0
    def bc_right_fn(t):
        return 1.0 if t >= t_switch else 0.0
        
    # 2. Run Hyperbolic subcritical solver at Fr = 0.2
    Fr_base = 0.2
    u_base = Fr_base * c0
    c_up_base = c0 - u_base
    
    _, times, eta_hist = solve_hyperbolic_shallow_water(
        u_base, g, H, L, nx, dt, n_steps, bc_right_fn
    )
    
    eta_obs = eta_hist[:, obs_idx]
    
    # Calculate theoretical delay
    tau_theoretical = (L - x_obs) / c_up_base
    
    # Measure onset delay using a midpoint (0.5) threshold (extremely accurate for advection)
    threshold = 0.5
    arrival_idx = np.where(eta_obs > threshold)[0]
    if len(arrival_idx) > 0:
        t_arrival = times[arrival_idx[0]]
        tau_measured = t_arrival - t_switch
    else:
        tau_measured = -1
        
    discrepancy_pct = abs(tau_measured - tau_theoretical) / tau_theoretical * 100
    
    print("\n--- HYPERBOLIC VERIFICATION ---")
    print(f"Theoretical c_up: {c_up_base:.4f} m/s")
    print(f"Theoretical Onset Delay tau_theoretical: {tau_theoretical:.4f}s")
    print(f"Measured Onset Delay tau_measured (threshold 0.5): {tau_measured:.4f}s")
    print(f"Discrepancy: {discrepancy_pct:.2f}%")
    
    # Measure onset delay for 10% (0.1) threshold to show robustness
    arrival_idx_10 = np.where(eta_obs > 0.1)[0]
    tau_measured_10 = times[arrival_idx_10[0]] - t_switch if len(arrival_idx_10) > 0 else -1
    discrepancy_pct_10 = abs(tau_measured_10 - tau_theoretical) / tau_theoretical * 100
    print(f"Measured Onset Delay (threshold 0.1): {tau_measured_10:.4f}s (Discrepancy: {discrepancy_pct_10:.2f}%)")
    
    # 3. Run Parabolic pure-diffusion baseline
    D_base = 2.0
    _, _, q_hist = solve_parabolic_diffusion(
        D_base, L, nx, dt, n_steps, bc_right_fn
    )
    
    q_obs = q_hist[:, obs_idx]
    
    # Measure arrival in parabolic case under different thresholds
    print("\n--- PARABOLIC COMPARATOR ONSET (LEAKAGE) ---")
    for th in [1e-6, 1e-4, 1e-2, 0.1, 0.5]:
        p_arrival_idx = np.where(q_obs > th)[0]
        if len(p_arrival_idx) > 0:
            p_tau = times[p_arrival_idx[0]] - t_switch
            print(f"  Parabolic onset at threshold {th}: {p_tau:.4f}s")
        else:
            print(f"  Parabolic onset at threshold {th}: did not reach")
            
    # 4. Measure Mutual Information over time
    noise_std = 0.05
    mi_hyperbolic = [gaussian_binary_mi(val, noise_std) for val in eta_obs]
    mi_parabolic = [gaussian_binary_mi(val, noise_std) for val in q_obs]
    
    # 5. Show MI-vs-Fr regime transition sweep
    Fr_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
    mi_vs_Fr = []
    
    # Measure at a fixed observation time t_meas = 4.5s
    t_meas = 4.5
    meas_step = int(t_meas / dt)
    
    for Fr in Fr_values:
        u_sweep = Fr * c0
        _, _, sweep_eta = solve_hyperbolic_shallow_water(
            u_sweep, g, H, L, nx, dt, n_steps, bc_right_fn
        )
        eta_meas = sweep_eta[meas_step, obs_idx]
        mi_vs_Fr.append(gaussian_binary_mi(eta_meas, noise_std))
        
    print("\n--- MI VS FROUDE REGIME TRANSITION (measured at t = 4.5s) ---")
    for Fr, mi in zip(Fr_values, mi_vs_Fr):
        u_sw = Fr * c0
        tau_th = (L - x_obs) / (c0 - u_sw)
        arrival_t = t_switch + tau_th
        print(f"  Fr={Fr:.2f} (u={u_sw:.3f} m/s) | Theoretical arrival t={arrival_t:.2f}s | MI = {mi:.4f} bits")
        
    # Write JSON results
    today_str = datetime.date.today().strftime('%Y%m%d')
    json_dir = Path("/home/ian/projects/sandy-chaos/memory/research")
    json_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / f"subcritical_hyperbolic_results_{today_str}.json"
    
    results_dict = {
        "tau_measured": float(tau_measured),
        "tau_theoretical": float(tau_theoretical),
        "Fr_values": [float(val) for val in Fr_values],
        "MI values": [float(val) for val in mi_vs_Fr],
        "MI_values": [float(val) for val in mi_vs_Fr],
        "comparator MI": [float(gaussian_binary_mi(val, noise_std)) for val in q_obs[::10]], # downsampled for size
        "comparator_MI": [float(gaussian_binary_mi(val, noise_std)) for val in q_obs[::10]],
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, indent=2)
    print(f"\nSaved results JSON to {json_path}")
    
    # Plotting if Matplotlib is available
    if HAS_MPL:
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Panel 1: Signal Evolution over time
        axes[0].plot(times - t_switch, eta_obs, label="Hyperbolic (SW, Fr=0.2)", color="blue", linewidth=2)
        axes[0].plot(times - t_switch, q_obs, label="Parabolic (Diffusion, D=2)", color="red", linestyle="--", linewidth=2)
        axes[0].axvline(x=tau_theoretical, color="blue", linestyle=":", label=f"Theoretical Delay ({tau_theoretical:.2f}s)")
        axes[0].set_xlim(-0.5, 5.0)
        axes[0].set_ylim(-0.05, 1.05)
        axes[0].set_xlabel("Time since perturbation (s)")
        axes[0].set_ylabel("Signal Strength at x_obs = 2.0")
        axes[0].set_title("Signal Propagation Profile")
        axes[0].legend()
        axes[0].grid(True)
        
        # Panel 2: Mutual Information over time
        axes[1].plot(times - t_switch, mi_hyperbolic, label="Hyperbolic (SW, Fr=0.2)", color="blue", linewidth=2)
        axes[1].plot(times - t_switch, mi_parabolic, label="Parabolic (Diffusion, D=2)", color="red", linestyle="--", linewidth=2)
        axes[1].axvline(x=tau_theoretical, color="blue", linestyle=":", label=f"Theoretical Delay ({tau_theoretical:.2f}s)")
        axes[1].set_xlim(-0.5, 5.0)
        axes[1].set_ylim(-0.05, 1.05)
        axes[1].set_xlabel("Time since perturbation (s)")
        axes[1].set_ylabel("Mutual Information I(Q; B) [bits]")
        axes[1].set_title("Information Arrival (Mutual Information)")
        axes[1].legend()
        axes[1].grid(True)
        
        # Panel 3: MI-vs-Fr transition curve
        axes[2].plot(Fr_values, mi_vs_Fr, marker='o', color="purple", linewidth=2)
        # Mark base Fr
        axes[2].axvline(x=Fr_base, color="blue", linestyle="--", label="Base Fr = 0.2")
        axes[2].set_xlabel("Froude Number Fr")
        axes[2].set_ylabel("Mutual Information at t = 4.5s")
        axes[2].set_title("MI vs Froude Number Sweep")
        axes[2].legend()
        axes[2].grid(True)
        
        plt.tight_layout()
        plot_path_research = Path("/home/ian/projects/sandy-chaos/research/subcritical_hyperbolic_demo.png")
        plot_path_memory = Path("/home/ian/projects/sandy-chaos/memory/research/subcritical_hyperbolic_demo.png")
        plt.savefig(plot_path_research, dpi=150)
        plt.savefig(plot_path_memory, dpi=150)
        print(f"Saved plots to {plot_path_research} and {plot_path_memory}")
        
    else:
        print("Matplotlib not available. Skipping plot generation.")


if __name__ == "__main__":
    main()
