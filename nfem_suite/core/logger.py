import csv
import time
import os

class DataLogger:
    def __init__(self, filename="simulation_data.csv"):
        self.filename = filename
        self.start_time = time.time()
        
        # Create file and write header
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "sim_time", "kinetic_entropy", "energetic_entropy", "active_nodes"])
            
    def log(self, sim_time, k_entropy, e_entropy, active_nodes):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), sim_time, k_entropy, e_entropy, active_nodes])
