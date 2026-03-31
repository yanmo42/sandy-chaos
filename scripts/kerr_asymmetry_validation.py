#!/usr/bin/env python3
"""
Kerr Asymmetry Validation
=========================
Direct validation of Kerr geometry producing intrinsic proper-time asymmetry.
Simpler, more focused than full benchmark.
"""

import sys
import os
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cosmic_comm.physics.metric import KerrBlackHole
from cosmic_comm.physics.geodesics import GeodesicTracer


def compute_geodesic(metric, r_start, L, max_steps=2000):
    """Compute geodesic for given angular momentum L."""
    theta = np.pi/2  # Equatorial plane
    energy = 1.0
    
    # Get metric components
    g_inv = metric.inverse_metric_components(r_start, theta)
    
    # Initial 4-momentum
    pt = -energy
    pphi = L
    
    # Compute pr from null condition: g^μν p_μ p_ν = 0
    term = (g_inv['tt'] * pt**2 + 
            2 * g_inv['tphi'] * pt * pphi + 
            g_inv['phiphi'] * pphi**2)
    
    if term > 0:
        pr = -np.sqrt(abs(term / g_inv['rr']))  # Negative for inward motion
    else:
        pr = 0.0
    
    ptheta = 0.0
    
    initial_state = np.array([0.0, r_start, theta, 0.0, pt, pr, ptheta, pphi])
    
    # Trace geodesic
    tracer = GeodesicTracer(metric=metric, step_size=0.05)
    trajectory = tracer.trace(initial_state, max_steps=max_steps)
    
    return trajectory


def compute_asymmetry_metrics(metric, r_start=10.0):
    """Compute asymmetry metrics for Kerr spacetime."""
    # Test prograde and retrograde with same |L|
    L_pro = 2.0  # Prograde angular momentum
    L_retro = -2.0  # Retrograde angular momentum
    
    traj_pro = compute_geodesic(metric, r_start, L_pro)
    traj_retro = compute_geodesic(metric, r_start, L_retro)
    
    # Extract proper times
    time_pro = traj_pro.get('proper_time', np.nan)
    time_retro = traj_retro.get('proper_time', np.nan)
    
    # Compute asymmetry
    if np.isnan(time_pro) or np.isnan(time_retro) or (time_pro + time_retro) == 0:
        asymmetry = np.nan
    else:
        asymmetry = (time_pro - time_retro) / ((time_pro + time_retro) / 2)
    
    return {
        'proper_time_prograde': float(time_pro),
        'proper_time_retrograde': float(time_retro),
        'proper_time_asymmetry': float(asymmetry),
        'status_prograde': traj_pro.get('status', 'unknown'),
        'status_retrograde': traj_retro.get('status', 'unknown')
    }


def simulate_flat_space_asymmetry(r_start=10.0):
    """Simulate what flat-space model could achieve."""
    # In flat space, prograde and retrograde would be symmetric
    # But we can try to create asymmetry with different effective velocities
    base_time = 10.0  # Base propagation time
    
    # Try to match Kerr asymmetry with flat-space model
    # Simple model: different effective speeds
    results = []
    
    for v in [0.1, 0.3, 0.5, 0.7, 0.9]:
        # Lorentz factor
        gamma = 1 / np.sqrt(1 - v**2)
        
        # Time dilation could create asymmetry if frames are boosted differently
        # But in flat space, symmetry can be restored by boost
        time_pro_flat = base_time / gamma  # Co-moving frame
        time_retro_flat = base_time * gamma  # Counter-moving frame
        
        asymmetry_flat = (time_pro_flat - time_retro_flat) / ((time_pro_flat + time_retro_flat) / 2)
        
        results.append({
            'boost_velocity': v,
            'time_prograde': time_pro_flat,
            'time_retrograde': time_retro_flat,
            'asymmetry': asymmetry_flat
        })
    
    return results


def main():
    """Main validation routine."""
    print("=" * 60)
    print("KERR ASYMMETRY VALIDATION")
    print("Validating intrinsic proper-time asymmetry in Kerr spacetime")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path('memory/research/kerr_asymmetry_2026-03')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test different spin parameters
    spins = [0.1, 0.3, 0.5, 0.7, 0.9]
    results = {}
    
    print("\nTesting Kerr geometry with different spin parameters:")
    print("Spin (a/M) | Prograde Time | Retrograde Time | Asymmetry | Status")
    print("-" * 70)
    
    for spin in spins:
        metric = KerrBlackHole(M=1.0, a=spin)
        metrics = compute_asymmetry_metrics(metric)
        
        results[f'spin_{spin}'] = {
            'spin_a/M': spin,
            **metrics
        }
        
        print(f"{spin:9.1f} | {metrics['proper_time_prograde']:13.2f} | "
              f"{metrics['proper_time_retrograde']:15.2f} | "
              f"{metrics['proper_time_asymmetry']:9.3f} | "
              f"{metrics['status_prograde']}/{metrics['status_retrograde']}")
    
    # Simulate flat-space attempts
    print("\n\nFlat-space model attempts (boosted frames):")
    print("Boost v | Prograde Time | Retrograde Time | Asymmetry")
    print("-" * 60)
    
    flat_results = simulate_flat_space_asymmetry()
    for r in flat_results:
        print(f"{r['boost_velocity']:7.2f} | {r['time_prograde']:14.2f} | "
              f"{r['time_retrograde']:16.2f} | {r['asymmetry']:9.3f}")
    
    # Find best flat-space match for each Kerr configuration
    print("\n\nMatching flat-space to Kerr:")
    print("Spin | Kerr Asymmetry | Best Flat Asymmetry | Residual | Match Quality")
    print("-" * 80)
    
    match_analysis = {}
    
    for spin in spins:
        kerr_asymmetry = results[f'spin_{spin}']['proper_time_asymmetry']
        
        # Find flat model with closest asymmetry
        best_match = min(flat_results, 
                        key=lambda x: abs(x['asymmetry'] - kerr_asymmetry))
        
        residual = abs(best_match['asymmetry'] - kerr_asymmetry)
        relative_residual = residual / (abs(kerr_asymmetry) + 1e-10)
        
        match_quality = "POOR" if relative_residual > 0.1 else \
                       "FAIR" if relative_residual > 0.05 else \
                       "GOOD" if relative_residual > 0.01 else "EXACT"
        
        match_analysis[f'spin_{spin}'] = {
            'kerr_asymmetry': kerr_asymmetry,
            'flat_asymmetry': best_match['asymmetry'],
            'flat_boost_velocity': best_match['boost_velocity'],
            'absolute_residual': residual,
            'relative_residual': relative_residual,
            'match_quality': match_quality
        }
        
        print(f"{spin:4.1f} | {kerr_asymmetry:14.3f} | {best_match['asymmetry']:18.3f} | "
              f"{residual:8.3f} | {match_quality}")
    
    # Generate plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Kerr asymmetry vs spin
    ax = axes[0, 0]
    spins_list = [r['spin_a/M'] for r in results.values()]
    asymmetries = [r['proper_time_asymmetry'] for r in results.values()]
    ax.plot(spins_list, asymmetries, 'o-', linewidth=2, markersize=8)
    ax.set_xlabel('Spin a/M')
    ax.set_ylabel('Proper Time Asymmetry')
    ax.set_title('Kerr: Asymmetry vs Spin')
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Prograde vs retrograde times
    ax = axes[0, 1]
    times_pro = [r['proper_time_prograde'] for r in results.values()]
    times_retro = [r['proper_time_retrograde'] for r in results.values()]
    width = 0.35
    x = np.arange(len(spins_list))
    ax.bar(x - width/2, times_pro, width, label='Prograde', alpha=0.7)
    ax.bar(x + width/2, times_retro, width, label='Retrograde', alpha=0.7)
    ax.set_xlabel('Spin a/M')
    ax.set_ylabel('Proper Time')
    ax.set_title('Kerr: Prograde vs Retrograde Times')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{s:.1f}' for s in spins_list])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Flat-space attempts
    ax = axes[1, 0]
    flat_velocities = [r['boost_velocity'] for r in flat_results]
    flat_asymmetries = [r['asymmetry'] for r in flat_results]
    ax.plot(flat_velocities, flat_asymmetries, 's-', linewidth=2, markersize=6)
    ax.set_xlabel('Boost Velocity v')
    ax.set_ylabel('Asymmetry (flat model)')
    ax.set_title('Flat Space: Asymmetry vs Boost Velocity')
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Residual analysis
    ax = axes[1, 1]
    residuals = [m['relative_residual'] for m in match_analysis.values()]
    colors = ['red' if r > 0.05 else 'green' for r in residuals]
    ax.bar([f'{s:.1f}' for s in spins_list], residuals, color=colors)
    ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='5% threshold')
    ax.set_xlabel('Spin a/M')
    ax.set_ylabel('Relative Residual')
    ax.set_title('Kerr vs Best Flat Match: Residual')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = output_dir / 'kerr_asymmetry_validation.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    print(f"\nPlot saved to {plot_path}")
    
    # Save results
    all_results = {
        'validation_date': '2026-03-30',
        'purpose': 'Validate intrinsic proper-time asymmetry in Kerr spacetime',
        'kerr_results': results,
        'flat_space_models': flat_results,
        'match_analysis': match_analysis,
        'conclusion': {}
    }
    
    # Determine if validation passes
    significant_residuals = [m['relative_residual'] > 0.05 for m in match_analysis.values()]
    any_significant = any(significant_residuals)
    all_significant = all(significant_residuals)
    
    if any_significant:
        conclusion = "KERR VALIDATION PASSES: Geometry produces intrinsic asymmetry"
        if all_significant:
            detail = "All spin values show >5% residual vs best flat-space match"
        else:
            detail = f"{sum(significant_residuals)}/{len(significant_residuals)} spin values show >5% residual"
    else:
        conclusion = "KERR VALIDATION FAILS: No significant asymmetry vs flat-space models"
        detail = "All spin values match flat-space models within 5%"
    
    all_results['conclusion'] = {
        'overall': conclusion,
        'detail': detail,
        'any_significant_residual': any_significant,
        'all_significant_residuals': all_significant,
        'significance_threshold': 0.05
    }
    
    # Save to file
    results_path = output_dir / 'validation_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print("VALIDATION COMPLETE")
    print(f"{'='*60}")
    print(f"\nConclusion: {conclusion}")
    print(f"Detail: {detail}")
    print(f"\nResults saved to: {output_dir}")
    
    # Next steps
    if any_significant:
        print("\nNext steps:")
        print("1. Update theory-implementation matrix with validation evidence")
        print("2. Add row T-015: Kerr geometry produces intrinsic proper-time asymmetry")
        print("3. Reference this validation in math_foundations_zf.md §9")
    else:
        print("\nWARNING: Validation failed to detect qualitative difference.")
        print("Consider revising theoretical claims about Kerr-specific leverage.")
    
    return all_results


if __name__ == "__main__":
    main()