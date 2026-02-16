import numpy as np
from nfem_suite.config.settings import MAX_SOLAR_IRRADIANCE, GRID_WIDTH, GRID_HEIGHT

class SunlightSimulator:
    def __init__(self):
        self.time_offset = 0.0
        # Simple cloud noise parameters
        self.cloud_scale = 20.0 
        self.cloud_speed = 2.0

    def get_irradiance_at(self, x, y, time):
        """
        Returns solar irradiance (W/m^2) at position (x, y)
        Simulates moving clouds using sine waves as a simple noise proxy.
        """
        # Moving noise pattern
        noise_x = (x + time * self.cloud_speed) / self.cloud_scale
        noise_y = (y + time * self.cloud_speed * 0.5) / self.cloud_scale
        
        # Combine sine waves to create cloud-like blobs
        val = np.sin(noise_x) * np.cos(noise_y) + np.sin(noise_x * 0.5 + noise_y * 0.5)
        
        # Normalize to 0..1 range (approx)
        cloud_density = (val + 2) / 4.0 
        cloud_density = np.clip(cloud_density, 0.0, 1.0)
        
        # Invert: High density = Low light
        light_factor = 1.0 - (cloud_density * 0.8) # Clouds block up to 80% light
        
        return MAX_SOLAR_IRRADIANCE * light_factor
