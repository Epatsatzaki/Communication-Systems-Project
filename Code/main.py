import os
import csv
import shutil
import numpy as np
import matplotlib.pyplot as plt
from signal_engine import * 
from dataset_generator import *

def main():
    # Define which modulations you want to run
    # You can add all 16 here once you write them in signal_engine.py
    modulations_to_run = {
        "QPSK": generate_qpsk,
        "16-QAM": generate_16qam,
        # "64-QAM": generate_64qam, 
    }

    with open(LABEL_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "modulation", "snr", "phase_noise", "iq_imbalance", "jamming", "amp_distortion", "severity"])
        
        for name, func in modulations_to_run.items():
            generate_for_modulation(name, func, writer)

if __name__ == "__main__":
    main()