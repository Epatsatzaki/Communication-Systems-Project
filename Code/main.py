import os
import csv
from signal_engine import *
from dataset_generator import generate_for_modulation

# Ensure this matches your structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL_FILE = os.path.join(BASE_DIR, "labels.csv")

def main():
    print("--- Starting Dataset Generation ---")
    
    modulations_to_run = {
        "QPSK":    generate_qpsk,
        "16-QAM":  lambda n: generate_generic_qam(n, 16),
        "32-QAM":  lambda n: generate_cross_qam(n, 32),
        "64-QAM":  lambda n: generate_generic_qam(n, 64),
        "128-QAM": lambda n: generate_cross_qam(n, 128),
        "256-QAM": lambda n: generate_generic_qam(n, 256),
    }

    # Open CSV in write mode to start fresh
    with open(LABEL_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "modulation", "snr", "phase_noise", "iq_imbalance", "jamming", "amp_distortion", "severity"])
        
        for name, gen_func in modulations_to_run.items():
            # This line MUST be here to trigger the work
            generate_for_modulation(name, gen_func, writer)

    print("--- All Datasets Complete ---")

# CRITICAL: This is what makes the script run when you type 'python3 main.py'
if __name__ == "__main__":
    main()