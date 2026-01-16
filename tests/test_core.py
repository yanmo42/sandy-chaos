
import sys
import os
import unittest
import numpy as np

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nfem_suite.core.network import Network
from nfem_suite.simulation.collapse_sim import CollapseSimulator
from nfem_suite.core.control import ControlSystem
from nfem_suite.simulation.sunlight_sim import SunlightSimulator
from nfem_suite.intelligence.vector_space import VectorSpace
from nfem_suite.intelligence.entropy_engine import EntropyEngine
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT, TIME_STEP

class TestNFEMCore(unittest.TestCase):
    def setUp(self):
        """Initialize all core components before each test."""
        self.network = Network()
        self.collapse_sim = CollapseSimulator(center_x=GRID_WIDTH/2, center_y=GRID_HEIGHT/2)
        self.control = ControlSystem()
        self.sunlight = SunlightSimulator()
        self.vector_space = VectorSpace()
        self.entropy_engine = EntropyEngine()
        
        # Add a few nodes for testing
        self.network.add_node(10, 10)
        self.network.add_node(20, 20)
        self.network.add_node(10, 20)
        self.network.add_node(20, 10) # Square formation

    def test_simulation_step(self):
        """Run a single simulation step and verify outputs."""
        t = 0.0
        
        # Update Control Target
        self.control.update_target(t)
        
        # Process Nodes
        for node in self.network.nodes:
            # 1. Physics
            v_flow = self.collapse_sim.get_velocity_at(node.position[0], node.position[1], t)
            v_control = self.control.get_control_vector(node)
            v_total = v_flow + v_control
            
            # 2. Energy
            irradiance = self.sunlight.get_irradiance_at(node.position[0], node.position[1], t)
            
            # Update Node
            node.update_physics(v_total, TIME_STEP)
            node.harvest_energy(irradiance, TIME_STEP)
            
            # Assertions for node state
            self.assertIsNotNone(node.position)
            self.assertIsNotNone(node.velocity)
            self.assertGreaterEqual(node.battery_level, 0)

        # Intelligence
        positions = self.network.get_positions()
        velocities = self.network.get_velocities()
        
        # Vector Space
        self.vector_space.compute_mesh(positions)
        gradients = self.vector_space.compute_gradients(positions, velocities)
        self.assertIsNotNone(gradients)
        
        # Entropy
        k_entropy = self.entropy_engine.calculate_kinetic_entropy(gradients)
        e_entropy = self.entropy_engine.calculate_energetic_entropy(self.network.nodes)
        s_entropy = self.entropy_engine.calculate_structural_entropy(self.vector_space.triangulation, positions)
        
        # Assertions for entropy
        self.assertIsInstance(k_entropy, float)
        self.assertIsInstance(e_entropy, float)
        self.assertIsInstance(s_entropy, float)
        
        print(f"\nTest Tick Successful:")
        print(f"K-Entropy: {k_entropy:.3f}")
        print(f"E-Entropy: {e_entropy:.3f}")
        print(f"S-Entropy: {s_entropy:.3f}")

if __name__ == '__main__':
    unittest.main()
