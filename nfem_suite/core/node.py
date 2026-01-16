import numpy as np
from nfem_suite.config.settings import BATTERY_CAPACITY, PV_EFFICIENCY, PING_COST

class SensorNode:
    def __init__(self, node_id, x, y):
        self.id = node_id
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([0.0, 0.0], dtype=float) # Measured flow velocity
        
        # Energy System
        self.battery_level = BATTERY_CAPACITY * 0.5 # Start at 50%
        self.pv_area = 0.1 # m^2
        self.is_active = True
    
    def update_physics(self, flow_vector, dt):
        """
        Updates the node's perceived flow velocity.
        In a real scenario, this is the sensor reading.
        In simulation, we adopt the flow vector of the environment.
        """
        # Clamp velocity to prevent explosion
        speed = np.linalg.norm(flow_vector)
        if speed > 50.0:
            flow_vector = flow_vector / speed * 50.0
            
        self.velocity = flow_vector
        # If the node is floating, update position based on flow
        self.position += self.velocity * dt
        
        # Soft boundary clamping (Bounce or Wrap?)
        # Let's just prevent them from going to infinity
        MAX_DIST = 10000.0
        if np.linalg.norm(self.position) > MAX_DIST:
             self.is_active = False # Disable lost nodes

    def harvest_energy(self, solar_irradiance, dt):
        """
        solar_irradiance: W/m^2
        """
        power_in = solar_irradiance * self.pv_area * PV_EFFICIENCY
        energy_gained = power_in * (dt / 3600.0) # Convert Joules/Ws to Wh
        
        self.battery_level = min(self.battery_level + energy_gained, BATTERY_CAPACITY)
        
        if self.battery_level > 0:
            self.is_active = True

    def consume_energy(self, amount):
        self.battery_level -= amount
        if self.battery_level <= 0:
            self.battery_level = 0
            self.is_active = False
            
    def ping(self):
        if self.is_active:
            self.consume_energy(PING_COST)
            return True
        return False
