from nfem_suite.core.node import SensorNode
import numpy as np

class Network:
    def __init__(self):
        self.nodes = []

    def add_node(self, x, y):
        new_id = len(self.nodes)
        node = SensorNode(new_id, x, y)
        self.nodes.append(node)
        return node

    def get_positions(self):
        return np.array([n.position for n in self.nodes])

    def get_velocities(self):
        return np.array([n.velocity for n in self.nodes])

    def get_active_nodes(self):
        return [n for n in self.nodes if n.is_active]

    def update(self, dt):
        # In a real distributed system, this is decentralized.
        # Here we manage the state updates centrally.
        pass
