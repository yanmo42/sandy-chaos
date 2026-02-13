"""
NFEM Suite - Niagara Falls Enthalpy Map
========================================
Main entry point for the enhanced simulation with:
- Enthalpy field (driving potential)
- Order-disorder duality space
- Complex entropy states
- Tachyonic loop detection
- Vortex-mediated A↔B communication

Run with: python -m nfem_suite.main
"""

import time
import sys
import matplotlib.pyplot as plt
import numpy as np

from nfem_suite.core.network import Network
from nfem_suite.simulation.collapse_sim import CollapseSimulator
from nfem_suite.simulation.sunlight_sim import SunlightSimulator
from nfem_suite.simulation.vortex_channel import VortexChannel
from nfem_suite.simulation.tachyonic_loop import TachyonicLoop
from nfem_suite.intelligence.vector_space import VectorSpace
from nfem_suite.intelligence.entropy_engine import EntropyEngine
from nfem_suite.intelligence.enthalpy_field import EnthalpyField
from nfem_suite.intelligence.duality_space import DualitySpace
from nfem_suite.visualization.dashboard import Dashboard
from nfem_suite.core.control import ControlSystem
from nfem_suite.core.logger import DataLogger
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT, TIME_STEP
from nfem_suite.formalization import registry


def main():
    print("=" * 70)
    print("NFEM Suite - Enthalpy Map & Duality Space Simulation")
    print("=" * 70)
    print(f"Active Formalization: {registry.get_active_name()}")
    print()
    
    # ========================================================================
    # SETUP
    # ========================================================================
    print("Initializing components...")
    
    # Core systems
    network = Network()
    collapse_sim = CollapseSimulator(center_x=GRID_WIDTH/2, center_y=GRID_HEIGHT/2)
    control = ControlSystem()
    sunlight = SunlightSimulator()
    
    # Intelligence layers
    vector_space = VectorSpace()
    entropy_engine = EntropyEngine()
    enthalpy_field = EnthalpyField(GRID_WIDTH, GRID_HEIGHT, resolution=50)
    duality_space = DualitySpace(history_length=1000)
    
    # Temporal & Communication
    tachyonic_loop = TachyonicLoop(max_loops=100)
    vortex_center = np.array([GRID_WIDTH/2, GRID_HEIGHT/2])
    vortex_channel = VortexChannel(vortex_center, vortex_radius=20.0, coupling_strength=1.0)
    
    # Logging & Visualization
    logger = DataLogger(filename="enthalpy_simulation_data.csv")
    
    # Deploy Sensor Array (Grid Pattern)
    print("Deploying sensor array...")
    grid_res = 10
    for x in np.linspace(0, GRID_WIDTH, grid_res):
        for y in np.linspace(0, GRID_HEIGHT, grid_res):
            network.add_node(x, y)
    
    print(f"Deployed {len(network.nodes)} sensor nodes")
    
    # Set up vortex channel endpoints (upstream and downstream)
    vortex_channel.set_source_a(np.array([GRID_WIDTH * 0.3, GRID_HEIGHT * 0.5]))
    vortex_channel.set_receiver_b(np.array([GRID_WIDTH * 0.7, GRID_HEIGHT * 0.5]))
    
    # Visualization mode
    VISUALIZE = True  # Set to False for headless mode
    DASHBOARD_MODE = 'full'  # 'full' for 6-panel, 'simple' for 2-panel
    
    if VISUALIZE:
        print(f"Starting dashboard in '{DASHBOARD_MODE}' mode...")
        dashboard = Dashboard(mode=DASHBOARD_MODE)
    
    # ========================================================================
    # SIMULATION LOOP
    # ========================================================================
    t = 0.0
    iteration = 0
    print("\nStarting simulation loop...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # ================================================================
            # A. ENVIRONMENTAL SIMULATION & CONTROL
            # ================================================================
            
            # Update control system (moving target zone)
            control.update_target(t)
            
            # Process each node
            for node in network.nodes:
                if not node.is_active:
                    continue
                
                # 1. Natural physics (entropic collapse)
                v_flow = collapse_sim.get_velocity_at(node.position[0], node.position[1], t)
                
                # 2. Control intervention
                v_control = control.get_control_vector(node)
                
                # 3. Combine
                v_total = v_flow + v_control
                
                # 4. Energy environment
                irradiance = sunlight.get_irradiance_at(node.position[0], node.position[1], t)
                
                # Update node state
                node.update_physics(v_total, TIME_STEP)
                node.harvest_energy(irradiance, TIME_STEP)
                
                # Simulate communication activity
                if np.random.random() < 0.1:
                    node.ping()
            
            # ================================================================
            # B. NETWORK INTELLIGENCE
            # ================================================================
            
            positions = network.get_positions()
            velocities = network.get_velocities()
            
            # 1. Spatial mesh (Delaunay)
            vector_space.compute_mesh(positions)
            
            # 2. Velocity gradients
            gradients = vector_space.compute_gradients(positions, velocities)
            
            # 3. Traditional entropy metrics
            k_entropy = entropy_engine.calculate_kinetic_entropy(gradients)
            e_entropy = entropy_engine.calculate_energetic_entropy(network.nodes)
            s_entropy = entropy_engine.calculate_structural_entropy(
                vector_space.triangulation, positions
            )
            
            # ================================================================
            # C. NEW INTELLIGENCE LAYERS
            # ================================================================
            
            # 1. Enthalpy Field (Driving Potential)
            enthalpy_field.update(positions, velocities)
            enthalpy_stats = enthalpy_field.get_statistics()
            
            # 2. Duality Space (Order-Disorder & Complex Entropy)
            duality_space.update(positions, velocities, gradients, t)
            duality_stats = duality_space.get_statistics()
            
            # 3. Tachyonic Loop Detection
            loop_data = tachyonic_loop.detect_and_close_loop(
                list(duality_space.position_history),
                list(duality_space.complex_state_history),
                list(duality_space.time_history),
                threshold=10.0,
                formalization=registry.get_active()
            )
            
            if loop_data:
                print(f"\n⚡ TEMPORAL LOOP DETECTED at t={t:.1f}s!")
                print(f"   ΔT = {loop_data['delta_t_real']:.3f} + {loop_data['delta_t_imag']:.3f}i")
                print(f"   |ΔT| = {loop_data['delta_t_magnitude']:.3f}")
                print(f"   Winding # = {loop_data['winding_number']:.2f}\n")
            
            # 4. Vortex Channel Communication
            # Inject test signals periodically
            if iteration % 10 == 0:
                signal_a = np.sin(t * 0.5)  # Oscillating signal from A
                vortex_channel.inject_signal_at_a(signal_a, t)
            
            if iteration % 15 == 5:
                signal_b = np.cos(t * 0.3)  # Different signal from B
                vortex_channel.inject_signal_at_b(signal_b, t)
            
            vortex_channel.update(t)
            channel_stats = vortex_channel.get_statistics()
            
            # ================================================================
            # D. LOGGING & OUTPUT
            # ================================================================
            
            active_count = len(network.get_active_nodes())
            
            # Extended logging
            logger.log(t, k_entropy, e_entropy, active_count)
            
            # Console output (every 50 iterations)
            if iteration % 50 == 0:
                print(f"t={t:6.1f}s | Nodes={active_count:3d} | "
                      f"K-Ent={k_entropy:.3f} | H̄={enthalpy_stats['mean_enthalpy']:.1f} | "
                      f"Ω={duality_stats['mean_order']:.3f} | "
                      f"Ω̄={duality_stats['mean_disorder']:.3f} | "
                      f"τ={abs(duality_space.emergent_time):.2f} | "
                      f"Winding={duality_space.winding_number:.2f} | "
                      f"Ch.Cap={channel_stats['channel_capacity']:.3f}")
            
            # ================================================================
            # E. VISUALIZATION
            # ================================================================
            
            if VISUALIZE:
                dashboard.update(
                    network=network,
                    gradients=gradients,
                    k_entropy=k_entropy,
                    e_entropy=e_entropy,
                    s_entropy=s_entropy,
                    triangulation=vector_space.triangulation,
                    time=t,
                    control=control,
                    enthalpy_field=enthalpy_field if DASHBOARD_MODE == 'full' else None,
                    duality_space=duality_space if DASHBOARD_MODE == 'full' else None,
                    vortex_channel=vortex_channel if DASHBOARD_MODE == 'full' else None
                )
            
            # Advance time
            t += TIME_STEP
            iteration += 1
            
            # Keep loop running at reasonable pace
            if not VISUALIZE:
                time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("Simulation stopped by user")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ Simulation Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # ================================================================
        # FINAL STATISTICS
        # ================================================================
        print("\n" + "=" * 70)
        print("FINAL STATISTICS")
        print("=" * 70)
        
        print("\nDuality Space:")
        for key, value in duality_stats.items():
            print(f"  {key}: {value:.4f}")
        
        print("\nEnthalpy Field:")
        for key, value in enthalpy_stats.items():
            print(f"  {key}: {value:.4f}")
        
        print("\nVortex Channel:")
        for key, value in channel_stats.items():
            print(f"  {key}: {value:.4f}")
        
        loop_stats = tachyonic_loop.get_loop_statistics()
        print("\nTachyonic Loops:")
        for key, value in loop_stats.items():
            print(f"  {key}: {value:.4f}")
        
        print("\n" + "=" * 70)
        print("Cleaning up...")
        
        if VISUALIZE:
            plt.close('all')
        
        print("Simulation complete.")
        print("=" * 70)


if __name__ == "__main__":
    main()
