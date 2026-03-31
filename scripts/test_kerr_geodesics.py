#!/usr/bin/env python3
"""Test Kerr geodesics computation."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from cosmic_comm.physics.metric import KerrBlackHole
from cosmic_comm.physics.geodesics import GeodesicTracer

print("Testing Kerr geodesics...")

# Create Kerr black hole with spin
metric = KerrBlackHole(M=1.0, a=0.9)
print(f"Created Kerr black hole: M={metric.M}, a={metric.a}")
print(f"Horizon radius: {metric.M + np.sqrt(metric.M**2 - metric.a**2)}")
print(f"Ergosphere radius (equatorial): {metric.ergosphere_radius(np.pi/2)}")

# Create tracer
tracer = GeodesicTracer(metric=metric, step_size=0.05)

# Test initial state for prograde photon
r = 10.0
theta = np.pi/2
energy = 1.0
L = 2.0  # Prograde angular momentum

# Get metric components
g = metric.metric_components(r, theta)
g_inv = metric.inverse_metric_components(r, theta)
print(f"\nMetric at r={r}, theta={theta}:")
print(f"  g_tt = {g['tt']}")
print(f"  g_tφ = {g['tphi']} (frame-dragging term)")
print(f"  g_φφ = {g['phiphi']}")

# Compute pr from null condition
pt = -energy
pphi = L
term = (g_inv['tt'] * pt**2 + 
        2 * g_inv['tphi'] * pt * pphi + 
        g_inv['phiphi'] * pphi**2)
print(f"\nNull condition term: {term}")
print(f"g^rr = {g_inv['rr']}")

if term > 0:
    pr = -np.sqrt(abs(term / g_inv['rr']))
else:
    pr = 0.0
    
ptheta = 0.0

initial_state = np.array([0.0, r, theta, 0.0, pt, pr, ptheta, pphi])
print(f"\nInitial state: {initial_state}")

# Trace geodesic
print("\nTracing geodesic...")
trajectory = tracer.trace(initial_state, max_steps=1000)
print(f"Status: {trajectory['status']}")
print(f"Proper time (affine parameter): {trajectory.get('proper_time', 'N/A')}")
print(f"Final phi: {trajectory['phi'][-1] if len(trajectory['phi']) > 0 else 'N/A'}")

# Test retrograde
print("\n\nTesting retrograde photon...")
L_retro = -2.0  # Retrograde angular momentum
term_retro = (g_inv['tt'] * pt**2 + 
              2 * g_inv['tphi'] * pt * L_retro + 
              g_inv['phiphi'] * L_retro**2)
if term_retro > 0:
    pr_retro = -np.sqrt(abs(term_retro / g_inv['rr']))
else:
    pr_retro = 0.0
    
initial_state_retro = np.array([0.0, r, theta, 0.0, pt, pr_retro, ptheta, L_retro])
trajectory_retro = tracer.trace(initial_state_retro, max_steps=1000)
print(f"Status: {trajectory_retro['status']}")
print(f"Proper time: {trajectory_retro.get('proper_time', 'N/A')}")

if 'proper_time' in trajectory and 'proper_time' in trajectory_retro:
    time_pro = trajectory['proper_time']
    time_retro = trajectory_retro['proper_time']
    asymmetry = (time_pro - time_retro) / ((time_pro + time_retro) / 2)
    print(f"\nProper time asymmetry: {asymmetry:.6f}")
    print(f"  Prograde: {time_pro:.6f}")
    print(f"  Retrograde: {time_retro:.6f}")