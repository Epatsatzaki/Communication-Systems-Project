import os
import pandas as pd

# Path to your generated images folder
BASE_DIR = '/home/evangelia/Documents/uni/3year/6sem/thlep/ergasia_erevnas_code/Images'
data_records = []

# Loop through each modulation folder (e.g., 16-QAM, 32-APSK)
for modulation in os.listdir(BASE_DIR):
    mod_path = os.path.join(BASE_DIR, modulation)
    if not os.path.isdir(mod_path): 
        continue
    
    for filename in os.listdir(mod_path):
        if filename.endswith(".png"):
            # Filename structure: {Modulation}_{Scenario}_{Index}.png
            # Example: 16-QPSK_Mixed_High_5.png
            name_parts = filename.replace(".png", "").split("_")
            
            # The scenario starts after the modulation name
            # Handling names like '16-QPSK' (index 0) and the rest is scenario
            scenario = "_".join(name_parts[1:-1]) 
            
            # Default values (No impairment)
            pn, iq, jam, amp, snr_range = 0, 0, 0, 0, "Clean"

            # Logic based on your specific scenario definitions
            if scenario == "PhaseNoiseOnly":
                pn, snr_range = 1, "Medium"
            elif scenario == "IQImbalanceOnly":
                iq, snr_range = 1, "Medium"
            elif scenario == "JammingOnly":
                jam, snr_range = 1, "Medium"
            elif scenario == "Mixed_Medium":
                snr_range, pn, iq = "Medium", 1, 1
            elif scenario == "Mixed_High":
                snr_range, pn, iq, jam, amp = "High", 1, 1, 1, 1
            elif scenario == "Clean":
                snr_range = "High" # Clean signals usually represent high SNR

            data_records.append({
                "filename": filename,
                "modulation": modulation,
                "scenario": scenario,
                "snr_level": snr_range,
                "phase_noise": pn,
                "iq_imbalance": iq,
                "jamming": jam,
                "amplitude_dist": amp,
                "path": os.path.join(modulation, filename)
            })

# Create the DataFrame
df = pd.DataFrame(data_records)

# Save for training
df.to_csv("master_dataset.csv", index=False)

print(f"Master CSV created with {len(df)} samples.")
print(df.head())