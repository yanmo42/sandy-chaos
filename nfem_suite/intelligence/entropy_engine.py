import numpy as np

class EntropyEngine:
    def __init__(self):
        pass
        
    def calculate_kinetic_entropy(self, gradients):
        """
        Calculates the entropy based on the distribution of velocity gradients (shear).
        """
        if not gradients:
            return 0.0
            
        grad_values = np.array([g['gradient'] for g in gradients])
        
        # We bin the gradients to create a probability distribution
        counts, _ = np.histogram(grad_values, bins=10, density=True)
        
        # Remove zeros to avoid log(0)
        p = counts[counts > 0]
        
        # Shannon Entropy
        entropy = -np.sum(p * np.log(p))
        return entropy

    def calculate_energetic_entropy(self, nodes):
        """
        Calculates entropy based on the distribution of energy levels.
        High entropy here might mean high inequality in energy distribution.
        """
        batteries = np.array([n.battery_level for n in nodes if n.is_active])
        if len(batteries) == 0:
            return 0.0
            
        # Normalize
        total_energy = np.sum(batteries)
        if total_energy == 0:
            return 0.0
            
        p = batteries / total_energy
        p = p[p > 0]
        
        entropy = -np.sum(p * np.log(p))
        return entropy

    def calculate_structural_entropy(self, triangulation, positions):
        """
        Calculates the entropy of the mesh structure itself.
        Measures the disorder in the distribution of plane (triangle) areas.
        """
        if triangulation is None or len(positions) < 3:
            return 0.0
            
        # Calculate area of each triangle
        areas = []
        for simplex in triangulation.simplices:
            # Get vertices
            pts = positions[simplex]
            # Area = 0.5 * |(xB - xA)(yC - yA) - (xC - xA)(yB - yA)|
            # Using cross product for 2D vectors (z-component)
            v1 = pts[1] - pts[0]
            v2 = pts[2] - pts[0]
            area = 0.5 * np.abs(np.cross(v1, v2))
            areas.append(area)
            
        areas = np.array(areas)
        total_area = np.sum(areas)
        
        if total_area == 0:
            return 0.0
            
        # Normalize to probability distribution
        p = areas / total_area
        p = p[p > 0] # Filter zeros
        
        # Shannon Entropy
        entropy = -np.sum(p * np.log(p))
        return entropy
