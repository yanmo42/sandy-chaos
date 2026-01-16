import time
import sys
import matplotlib.pyplot as plt
import numpy as np
from nfem_suite.core.network import Network
from nfem_suite.simulation.whirlpool_sim import WhirlpoolSimulator
from nfem_suite.simulation.collapse_sim import CollapseSimulator
from nfem_suite.simulation.sunlight_sim import SunlightSimulator
from nfem_suite.intelligence.vector_space import VectorSpace
from nfem_suite.intelligence.entropy_engine import EntropyEngine
from nfem_suite.visualization.dashboard import Dashboard
from nfem_suite.core.control import ControlSystem
from nfem_suite.core.logger import DataLogger
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT, TIME_STEP

def main():
    print("Initializing NFEM Suite...")
    
    # 1. Setup
    network = Network()
    # whirlpool = WhirlpoolSimulator(center_x=GRID_WIDTH/2, center_y=GRID_HEIGHT/2)
    collapse_sim = CollapseSimulator(center_x=GRID_WIDTH/2, center_y=GRID_HEIGHT/2)
    control = ControlSystem()
    sunlight = SunlightSimulator()
    vector_space = VectorSpace()
    entropy_engine = EntropyEngine()
    logger = DataLogger()
    
    # 2. Deploy Sensors (Grid Pattern)
    print("Deploying Sensor Array...")
    grid_res = 10
    for x in np.linspace(0, GRID_WIDTH, grid_res):
        for y in np.linspace(0, GRID_HEIGHT, grid_res):
            network.add_node(x, y)
            
    # Optional: Visualization (Set to False for headless)
    VISUALIZE = True
    if VISUALIZE:
        dashboard = Dashboard()
    
    # 3. Simulation Loop
    t = 0.0
    print("Starting Simulation Loop...")
    
    try:
        while True:
            # A. Environmental Simulation & Control
            # ---------------------------
            # Update Control System Target (The "Hot Potato")
            control.update_target(t)

            # For each node, calculate the local physics + control input
            for node in network.nodes:
                if not node.is_active:
                    continue
                    
                # 1. Natural Physics (Entropic Collapse)
                v_flow = collapse_sim.get_velocity_at(node.position[0], node.position[1], t)
                
                # 2. Control Intervention
                v_control = control.get_control_vector(node)
                
                # Combine
                v_total = v_flow + v_control

                # 3. Energy Environment
                irradiance = sunlight.get_irradiance_at(node.position[0], node.position[1], t)
                
                # Update Node State
                node.update_physics(v_total, TIME_STEP)
                node.harvest_energy(irradiance, TIME_STEP)
                
                # Random ping to simulate network activity
                if np.random.random() < 0.1:
                    node.ping()

            # B. Network Intelligence
            # -----------------------
            positions = network.get_positions()
            velocities = network.get_velocities()
            
            # 1. Connect the Dots (Mesh)
            vector_space.compute_mesh(positions)
            
            # 2. Calculate Gradients (Vector Field Analysis)
            gradients = vector_space.compute_gradients(positions, velocities)
            
            # 3. Calculate Entropy
            k_entropy = entropy_engine.calculate_kinetic_entropy(gradients)
            e_entropy = entropy_engine.calculate_energetic_entropy(network.nodes)
            s_entropy = entropy_engine.calculate_structural_entropy(vector_space.triangulation, positions)
            
            # 4. Logging
            active_count = len(network.get_active_nodes())
            logger.log(t, k_entropy, e_entropy, active_count)
            
            # C. Visualization / Output
            # -------------------------
            if VISUALIZE:
                dashboard.update(network, gradients, k_entropy, e_entropy, s_entropy, vector_space.triangulation, t, control)
            else:
                print(f"Time: {t:.1f}s | Kinetic: {k_entropy:.3f} | Struct: {s_entropy:.3f}")

            t += TIME_STEP
            
            # Keep the loop running at a reasonable pace
            if not VISUALIZE:
                time.sleep(0.1) 
                
    except KeyboardInterrupt:
        print("\nSimulation Stopped by User.")
    except Exception as e:
        print(f"\nSimulation Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        if VISUALIZE:
            plt.close('all')

if __name__ == "__main__":
    main()
