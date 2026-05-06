import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import signal_engine as engine 

# --- CONFIGURATION DICTIONARY ---
# Each entry contains: Generation function, Demodulation logic, and Exact Theory
MOD_CONFIG = {
    "QPSK": {
        "gen": engine.generate_qpsk,
        "demod": lambda syms: (np.sign(np.real(syms)) + 1j * np.sign(np.imag(syms))) / np.sqrt(2),
        "theory": lambda snr_lin: erfc(np.sqrt(snr_lin / 2)) - 0.25 * (erfc(np.sqrt(snr_lin / 2)))**2,
        "snr_range": np.arange(0, 16, 2),
        "pn_list": [0, 5, 10]
    },
    "16-QAM": {
        "gen": engine.generate_16qam,
        "demod": engine.demodulate_16qam, # Assuming this is in your signal_engine.py
        "theory": lambda snr_lin: 1.5 * erfc(np.sqrt(snr_lin / 10)),
        "snr_range": np.arange(0, 22, 2), # 16-QAM needs more SNR
        "pn_list": [0, 2, 5] # 16-QAM is more sensitive to phase noise
    },
    "64-QAM": {
        "gen": lambda n: generate_generic_qam(n, 64),
        "demod": lambda s: demodulate_generic_qam(s, 64),
        "theory": lambda snr_lin: (7/4) * erfc(np.sqrt(snr_lin / 42)),
        "snr_range": np.arange(0, 26, 2),
        "pn_list": [0, 1, 2] # Very sensitive!
    },
    "256-QAM": {
        "gen": lambda n: generate_generic_qam(n, 256),
        "demod": lambda s: demodulate_generic_qam(s, 256),
        "theory": lambda snr_lin: (15/8) * erfc(np.sqrt(snr_lin / 170)),
        "snr_range": np.arange(10, 32, 2),
        "pn_list": [0, 0.5, 1] # Extremely sensitive!
    },
    "4-HQAM": { # Often treated as QPSK with a specific offset
        "gen": engine.generate_qpsk, 
        "demod": MOD_CONFIG["QPSK"]["demod"],
        "theory": MOD_CONFIG["QPSK"]["theory"],
        "snr_range": np.arange(0, 16, 2),
        "pn_list": [0, 5, 10]
    }
}

def run_simulation(mod_name, snr_db, pn_std_deg):
    num_symbols = 1000000 
    config = MOD_CONFIG[mod_name]
    
    # 1. Generate dynamically
    tx = config["gen"](num_symbols)
    
    # 2. Apply Impairments
    rx = engine.apply_phase_noise(tx, pn_std_deg)
    rx = engine.apply_awgn(rx, snr_db)
    
    # 3. Demodulate dynamically
    decoded = config["demod"](rx)
    
    # 4. Count Errors
    errors = np.sum(np.abs(tx - decoded) > 0.01)
    return errors / num_symbols

def plot_performance(mod_name):
    config = MOD_CONFIG[mod_name]
    snr_range = config["snr_range"]
    
    plt.figure(figsize=(10, 7))
    
    # Theoretical Baseline
    snr_lin_fine = 10**(np.linspace(snr_range[0], snr_range[-1], 100) / 10.0)
    plt.semilogy(np.linspace(snr_range[0], snr_range[-1], 100), 
                 config["theory"](snr_lin_fine), 'k--', label=f'Theoretical {mod_name}')
    
    # Simulation Loops
    for pn in config["pn_list"]:
        print(f"Simulating {mod_name} | Phase Noise: {pn}°...")
        sep_results = [run_simulation(mod_name, snr, pn) for snr in snr_range]
        plt.semilogy(snr_range, sep_results, 'o-', label=f'Simulated PN={pn}°')

    plt.grid(True, which='both')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Symbol Error Probability (SEP)')
    plt.title(f'{mod_name} SEP vs SNR in Presence of Phase Noise')
    plt.legend()
    plt.ylim([1e-5, 1])
    plt.show()

if __name__ == "__main__":
    # Just change this string to switch the whole script!
    plot_performance("16-QAM")