"""
Enthalpy Field Module
=====================
Computes the enthalpy field H(x,t) and its gradient ∇H across the system.

Enthalpy is the thermodynamic potential that *drives* entropy flow:
    H = U + PV
    
Where:
- U = Internal energy (kinetic + potential)
- P = Pressure (from node density, flow compression)
- V = Volume (local region)

The enthalpy gradient ∇H indicates:
- Direction of entropy production
- Magnitude of thermodynamic driving force
- Where order → disorder transitions occur

This is the "Enthalpy Map" - showing the potential landscape that governs
the system's entropic evolution.
"""

import numpy as np
from scipy.spatial import cKDTree
from typing import List, Tuple, Dict, Any


class EnthalpyField:
    """
    Computes and manages the enthalpy field H(x,t) and its spatial gradient.
    
    The enthalpy field reveals the thermodynamic potential landscape that
    drives entropy production in the system.
    """
    
    def __init__(self, grid_width: float, grid_height: float, 
                 resolution: int = 50, density: float = 1000.0):
        """
        Initialize the enthalpy field.
        
        Args:
            grid_width: Width of simulation domain
            grid_height: Height of simulation domain
            resolution: Grid resolution for field computation
            density: Fluid density (kg/m³)
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.resolution = resolution
        self.density = density
        
        # Create grid for field evaluation
        x = np.linspace(0, grid_width, resolution)
        y = np.linspace(0, grid_height, resolution)
        self.grid_x, self.grid_y = np.meshgrid(x, y)
        
        # Storage for computed fields
        self.enthalpy_field = np.zeros((resolution, resolution))
        self.gradient_field = np.zeros((resolution, resolution, 2))
        
        # Parameters for pressure computation
        self.pressure_scale = 100.0  # Pa per unit density
        self.volume_element = (grid_width / resolution) * (grid_height / resolution)
    
    def compute_kinetic_energy_density(self, positions: np.ndarray, 
                                      velocities: np.ndarray) -> np.ndarray:
        """
        Compute kinetic energy density field U_kinetic = (1/2) ρ |v|²
        
        Uses KDTree for efficient spatial interpolation.
        
        Args:
            positions: Node positions (N x 2)
            velocities: Node velocities (N x 2)
        
        Returns:
            2D array of kinetic energy density at each grid point
        """
        if len(positions) == 0:
            return np.zeros_like(self.grid_x)
        
        # Build spatial tree for efficient lookup
        tree = cKDTree(positions)
        
        # Flatten grid for querying
        grid_points = np.column_stack([self.grid_x.ravel(), self.grid_y.ravel()])
        
        # Find nearest neighbors (using k=3 for smoother interpolation)
        k = min(3, len(positions))
        distances, indices = tree.query(grid_points, k=k)
        
        # Inverse distance weighted interpolation of velocity
        kinetic_energy = np.zeros(len(grid_points))
        
        for i, (dists, idxs) in enumerate(zip(distances, indices)):
            if k == 1:
                # Single nearest neighbor
                vel = velocities[idxs]
                kinetic_energy[i] = 0.5 * self.density * np.dot(vel, vel)
            else:
                # Weighted average of k nearest neighbors
                weights = 1.0 / (dists + 1e-6)  # Inverse distance weighting
                weights /= np.sum(weights)
                
                avg_vel = np.sum(velocities[idxs] * weights[:, np.newaxis], axis=0)
                kinetic_energy[i] = 0.5 * self.density * np.dot(avg_vel, avg_vel)
        
        # Reshape back to grid
        return kinetic_energy.reshape(self.grid_x.shape)
    
    def compute_pressure_field(self, positions: np.ndarray) -> np.ndarray:
        """
        Compute pressure field P from node density.
        
        Pressure arises from:
        1. Node density (more nodes = higher pressure)
        2. Flow compression (nodes clustering)
        
        Uses kernel density estimation with Gaussian kernel.
        
        Args:
            positions: Node positions (N x 2)
        
        Returns:
            2D array of pressure at each grid point
        """
        if len(positions) == 0:
            return np.zeros_like(self.grid_x)
        
        # Build spatial tree
        tree = cKDTree(positions)
        
        # Flatten grid
        grid_points = np.column_stack([self.grid_x.ravel(), self.grid_y.ravel()])
        
        # Count neighbors within radius (kernel density)
        radius = min(self.grid_width, self.grid_height) / 10.0
        neighbor_counts = tree.query_ball_point(grid_points, radius, return_length=True)
        
        # Pressure proportional to local density
        pressure = self.pressure_scale * (neighbor_counts / len(positions))
        
        return pressure.reshape(self.grid_x.shape)
    
    def compute_enthalpy(self, positions: np.ndarray, velocities: np.ndarray) -> np.ndarray:
        """
        Compute total enthalpy field: H = U + PV
        
        Args:
            positions: Node positions (N x 2)
            velocities: Node velocities (N x 2)
        
        Returns:
            2D array of enthalpy at each grid point
        """
        # Internal energy (kinetic)
        U = self.compute_kinetic_energy_density(positions, velocities)
        
        # Pressure
        P = self.compute_pressure_field(positions)
        
        # Enthalpy: H = U + PV
        H = U + P * self.volume_element
        
        self.enthalpy_field = H
        return H
    
    def compute_gradient(self) -> np.ndarray:
        """
        Compute spatial gradient ∇H of the enthalpy field.
        
        The gradient points in the direction of maximum enthalpy increase,
        which indicates the direction of entropy production.
        
        Returns:
            3D array (resolution x resolution x 2) of gradient vectors [∂H/∂x, ∂H/∂y]
        """
        # Compute gradients using central differences
        dy, dx = np.gradient(self.enthalpy_field)
        
        # Scale by grid spacing
        dx_spacing = self.grid_width / self.resolution
        dy_spacing = self.grid_height / self.resolution
        
        dx /= dx_spacing
        dy /= dy_spacing
        
        # Stack into vector field
        self.gradient_field = np.stack([dx, dy], axis=-1)
        
        return self.gradient_field
    
    def update(self, positions: np.ndarray, velocities: np.ndarray):
        """
        Update the enthalpy field and its gradient.
        
        Args:
            positions: Current node positions
            velocities: Current node velocities
        """
        self.compute_enthalpy(positions, velocities)
        self.compute_gradient()
    
    def get_enthalpy_at(self, x: float, y: float) -> float:
        """
        Get enthalpy value at a specific point via bilinear interpolation.
        
        Args:
            x, y: Coordinates to sample
        
        Returns:
            Enthalpy value at (x, y)
        """
        # Convert to grid coordinates
        i = (y / self.grid_height) * (self.resolution - 1)
        j = (x / self.grid_width) * (self.resolution - 1)
        
        # Clamp to grid bounds
        i = np.clip(i, 0, self.resolution - 1)
        j = np.clip(j, 0, self.resolution - 1)
        
        # Bilinear interpolation
        i0, i1 = int(np.floor(i)), int(np.ceil(i))
        j0, j1 = int(np.floor(j)), int(np.ceil(j))
        
        if i0 == i1 and j0 == j1:
            return self.enthalpy_field[i0, j0]
        
        # Interpolation weights
        wi = i - i0
        wj = j - j0
        
        # Bilinear
        h = (1 - wi) * (1 - wj) * self.enthalpy_field[i0, j0] + \
            (1 - wi) * wj * self.enthalpy_field[i0, j1] + \
            wi * (1 - wj) * self.enthalpy_field[i1, j0] + \
            wi * wj * self.enthalpy_field[i1, j1]
        
        return h
    
    def get_gradient_at(self, x: float, y: float) -> np.ndarray:
        """
        Get gradient vector at a specific point via bilinear interpolation.
        
        Args:
            x, y: Coordinates to sample
        
        Returns:
            Gradient vector [∂H/∂x, ∂H/∂y] at (x, y)
        """
        # Convert to grid coordinates
        i = (y / self.grid_height) * (self.resolution - 1)
        j = (x / self.grid_width) * (self.resolution - 1)
        
        # Clamp
        i = np.clip(i, 0, self.resolution - 1)
        j = np.clip(j, 0, self.resolution - 1)
        
        # Interpolate
        i0, i1 = int(np.floor(i)), int(np.ceil(i))
        j0, j1 = int(np.floor(j)), int(np.ceil(j))
        
        if i0 == i1 and j0 == j1:
            return self.gradient_field[i0, j0]
        
        wi = i - i0
        wj = j - j0
        
        grad = (1 - wi) * (1 - wj) * self.gradient_field[i0, j0] + \
               (1 - wi) * wj * self.gradient_field[i0, j1] + \
               wi * (1 - wj) * self.gradient_field[i1, j0] + \
               wi * wj * self.gradient_field[i1, j1]
        
        return grad
    
    def compute_entropy_production_rate(self) -> float:
        """
        Compute the total entropy production rate across the field.
        
        Entropy production ∝ |∇H|² (dissipation from gradients)
        
        Returns:
            Scalar entropy production rate
        """
        # Magnitude of gradient at each point
        grad_magnitude = np.linalg.norm(self.gradient_field, axis=-1)
        
        # Total dissipation (squared gradients integrated)
        total_dissipation = np.sum(grad_magnitude**2)
        
        # Normalize by grid size
        entropy_rate = total_dissipation / (self.resolution**2)
        
        return entropy_rate
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Get statistical summary of the enthalpy field.
        
        Returns:
            Dictionary with statistics (mean, max, min, gradient_norm)
        """
        grad_magnitude = np.linalg.norm(self.gradient_field, axis=-1)
        
        return {
            'mean_enthalpy': np.mean(self.enthalpy_field),
            'max_enthalpy': np.max(self.enthalpy_field),
            'min_enthalpy': np.min(self.enthalpy_field),
            'std_enthalpy': np.std(self.enthalpy_field),
            'mean_gradient': np.mean(grad_magnitude),
            'max_gradient': np.max(grad_magnitude),
            'entropy_production': self.compute_entropy_production_rate()
        }
