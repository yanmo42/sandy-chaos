import numpy as np
from scipy.spatial import Delaunay

class VectorSpace:
    def __init__(self):
        self.triangulation = None
        self.edges = []
        
    def compute_mesh(self, positions):
        """
        Computes Delaunay Triangulation for the given node positions.
        Returns the simplexes (triangles).
        """
        if len(positions) < 4:
            return None
            
        try:
            # "QJ" joggles inputs to avoid precision errors with flat/collinear data
            self.triangulation = Delaunay(positions, qhull_options="QJ")
        except Exception as e:
            print(f"Warning: Mesh computation failed: {e}")
            self.triangulation = None
            
        return self.triangulation
    
    def compute_gradients(self, positions, velocities):
        """
        Calculates velocity gradients (shear) across the connected edges.
        Returns a list of (node_i, node_j, gradient_magnitude).
        """
        if self.triangulation is None:
            return []
            
        gradients = []
        # Extract unique edges from triangulation
        # Delaunay.simplices is an array of shape (ntriangles, 3)
        # We need to extract unique pairs
        edges = set()
        for simplex in self.triangulation.simplices:
            edges.add(tuple(sorted((simplex[0], simplex[1]))))
            edges.add(tuple(sorted((simplex[1], simplex[2]))))
            edges.add(tuple(sorted((simplex[2], simplex[0]))))
            
        for i, j in edges:
            pos_i = positions[i]
            pos_j = positions[j]
            vel_i = velocities[i]
            vel_j = velocities[j]
            
            # Distance
            dist = np.linalg.norm(pos_j - pos_i)
            if dist == 0: continue
            
            # Velocity difference
            vel_diff = np.linalg.norm(vel_j - vel_i)
            
            # Gradient (Shear) = dV / dX
            gradient = vel_diff / dist
            
            gradients.append({
                'u': i, 'v': j, 
                'gradient': gradient,
                'pos_u': pos_i, 'pos_v': pos_j
            })
            
        return gradients
