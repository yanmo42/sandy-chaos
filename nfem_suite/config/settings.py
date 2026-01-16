# Global Settings for NFEM Simulation

# Simulation Space
GRID_WIDTH = 100.0  # meters
GRID_HEIGHT = 100.0 # meters
TIME_STEP = 0.1     # seconds

# Physics Constants
GRAVITY = 9.81
WATER_DENSITY = 1000.0 # kg/m^3

# Photovoltaic Settings
PV_EFFICIENCY = 0.20 # 20% efficiency
MAX_SOLAR_IRRADIANCE = 1000.0 # W/m^2 (Peak Sun)
BATTERY_CAPACITY = 100.0 # Watt-hours

# Sensor Network
PING_COST = 0.5 # Energy cost to ping neighbors (Watts/ping)
COMM_RANGE = 15.0 # meters
