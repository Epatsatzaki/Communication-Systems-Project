import os
import csv
import shutil
import numpy as np
import matplotlib.pyplot as plt
from signal_engine import * 

# 1. FIX PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL_FILE = os.path.join(BASE_DIR, "labels.csv")
NUM_SAMPLES_PER_TYPE = 60

def setup_modulation_folder(mod_name):
    """Creates a specific folder for the modulation."""
    path = os.path.join(BASE_DIR, "Images", mod_name)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return path

def save_constellation(symbols, filename):
    plt.figure(figsize=(3, 3), dpi=100)
    plt.scatter(np.real(symbols), np.imag(symbols), s=0.8, c='black')
    plt.xlim([-2.5, 2.5])
    plt.ylim([-2.5, 2.5])
    plt.axis('off') 
    plt.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()

def generate_for_modulation(mod_name, gen_function, writer):
    """Generates all scenarios for a single modulation type."""
    output_dir = setup_modulation_folder(mod_name)
    scenarios = ["Clean", "PhaseNoiseOnly", "IQImbalanceOnly", "JammingOnly", "Mixed_Medium", "Mixed_High"]
    
    print(f"Starting modulation: {mod_name}")
    
    for scenario in scenarios:
        for i in range(NUM_SAMPLES_PER_TYPE):
            # Defaults
            snr, pn, iq_a, iq_p, jam, amp_dist = 35, 0, 0, 0, -100, 0
            sev = "None"

            # Your existing parameter logic
            if scenario == "PhaseNoiseOnly":
                pn, sev = np.random.uniform(5, 12), "Medium"
            elif scenario == "IQImbalanceOnly":
                iq_a, iq_p, sev = np.random.uniform(0.8, 1.5), np.random.uniform(5, 12), "Medium"
            elif scenario == "JammingOnly":
                jam, sev = np.random.uniform(-18, -12), "Medium"
            elif scenario == "Mixed_Medium":
                snr, pn, iq_a, iq_p, sev = np.random.uniform(12, 18), np.random.uniform(2, 6), np.random.uniform(0.3, 0.7), np.random.uniform(2, 5), "Medium"
            elif scenario == "Mixed_High":
                snr, pn, iq_a, iq_p, jam, amp_dist, sev = np.random.uniform(5, 10), np.random.uniform(8, 18), np.random.uniform(1.0, 2.5), np.random.uniform(8, 20), np.random.uniform(-15, -10), 0.2, "High"

            # Process Signal
            sig = gen_function(1000) # Calls the specific modulation function
            if pn > 0: sig = apply_phase_noise(sig, pn)
            if iq_a > 0 or iq_p > 0: sig = apply_iq_imbalance(sig, iq_a, iq_p)
            if amp_dist > 0: sig = apply_amplitude_distortion(sig, amp_dist)
            if jam > -100: sig = apply_jamming(sig, jam)
            sig = apply_awgn(sig, snr)

            img_name = f"{mod_name}_{scenario}_{i}.png"
            save_constellation(sig, os.path.join(output_dir, img_name))
            
            writer.writerow([img_name, mod_name, f"{int(snr)}dB", "Yes" if pn > 0 else "No", "Yes" if (iq_a > 0 or iq_p > 0) else "No", "Yes" if jam > -100 else "No", "Yes" if amp_dist > 0 else "No", sev])
