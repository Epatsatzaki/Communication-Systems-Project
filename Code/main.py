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
        """
            # Existing ones
    "QPSK": lambda n: engine.generate_qpsk(n),
    "16-QAM": lambda n: engine.generate_generic_qam(n, 16),
    "64-QAM": lambda n: engine.generate_generic_qam(n, 64),
    "16-HQAM": lambda n: engine.generate_hex_box_qam(n, 16),
    "64-HQAM": lambda n: engine.generate_hex_box_qam(n, 64),
    
    # New ASK modulations
    "4-ASK": lambda n: engine.generate_ask(n, 4),
    "8-ASK": lambda n: engine.generate_ask(n, 8),
    
    # New APSK modulations
    "16-APSK": lambda n: engine.generate_apsk(n, 16),
    "32-APSK": lambda n: engine.generate_apsk(n, 32),
    "64-APSK": lambda n: engine.generate_apsk(n, 64),
    "128-APSK": lambda n: engine.generate_apsk(n, 128)

    """
        
        
        "64-QAM": lambda n: generate_generic_qam(n, 64),
        "128-QAM": lambda n: generate_generic_qam(n, 128),
        "256-QAM": lambda n: generate_generic_qam(n, 256)
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