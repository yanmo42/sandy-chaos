import numpy as np
from nfem_suite.config.settings import GRID_WIDTH, GRID_HEIGHT

class ControlSystem:
    def __init__(self):
        self.target_pos = np.array([GRID_WIDTH/2, GRID_HEIGHT/2])
        self.target_radius = 15.0
        self.control_strength = 20.0
        self.orbit_speed = 0.2
        self.mode = "REPEL" # "STABILIZE", "EXCITE", "REPEL"

    def update_target(self, t):
        """
        Moves the control focus area dynamically.
        This simulates 'passing control around' the field.
        """
        # Lissajous figure for complex path
        self.target_pos[0] = GRID_WIDTH/2 + 30.0 * np.cos(t * self.orbit_speed)
        self.target_pos[1] = GRID_HEIGHT/2 + 20.0 * np.sin(t * self.orbit_speed * 1.3)

    def get_control_vector(self, node):
        """
        Calculates the control vector for a specific node.
        If the node is within the target radius, a force is applied.
        """
        dist = np.linalg.norm(node.position - self.target_pos)
        
        if dist < self.target_radius:
            # Calculate influence factor (stronger at center)
            influence = (self.target_radius - dist) / self.target_radius
            
            if self.mode == "STABILIZE":
                # Push nodes towards the control center (Grouping/Ordering)
                direction = self.target_pos - node.position
                norm = np.linalg.norm(direction)
                if norm > 0:
                    direction /= norm
                return direction * self.control_strength * influence
            
            elif self.mode == "EXCITE":
                # Add random noise
                return np.random.randn(2) * self.control_strength * influence

            elif self.mode == "REPEL":
                # "Poke": Push nodes AWAY from control center
                direction = node.position - self.target_pos
                norm = np.linalg.norm(direction)
                if norm > 0:
                    direction /= norm
                return direction * self.control_strength * influence
                
        return np.array([0.0, 0.0])
