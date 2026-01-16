# Niagara Falls Entropy Map (NFEM) Suite

This software suite simulates a sensor network monitoring a fluid dynamic system (Whirlpool) with self-sustaining photovoltaic nodes.

## Architecture

- **Core**: Defines the `SensorNode` (with PV and Battery logic) and `Network`.
- **Simulation**: Generates `Whirlpool` velocity fields with **Chaotic Folding** (time-dependent shear).
- **Control**: `ControlSystem` implements a "Hot Potato" protocol, moving a control zone dynamically to stabilize specific areas.
- **Intelligence**: 
  - `VectorSpace`: Connects nodes via Delaunay Triangulation and calculates velocity gradients (Shear/Folding).
  - `EntropyEngine`: Calculates the system's Kinetic Entropy (Turbulence) and Energetic Entropy (Inequality).
- **Visualization**: `Dashboard` provides real-time heatmap of folding intensity and tracks the control zone.

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r nfem_suite/requirements.txt
   ```

## Running the Simulation

Run the main entry point (ensure you are in the root directory):

```bash
export PYTHONPATH=$PYTHONPATH:.
python -m nfem_suite.main
```

## Configuration

Edit `nfem_suite/config/settings.py` to adjust:
- Grid size
- Physics constants
- PV Efficiency
- Simulation speed
