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
        "gen": lambda n: engine.generate_generic_qam(n, 16),
        "demod": lambda s: engine.demodulate_generic_qam(s, 16),
        # k = 3 / (2*(16-1)) = 3/30 = 0.1
        "theory": lambda snr_lin: 1.5 * erfc(np.sqrt(0.1 * snr_lin)) - 0.5625 * (erfc(np.sqrt(0.1 * snr_lin)))**2,
        "snr_range": np.arange(0, 22, 2),
        "pn_list": [0, 2, 5]
    },
    "32-QAM": {
        "gen": lambda n: engine.generate_cross_qam(n, 32),
        "demod": lambda s: engine.demodulate_cross_qam(s, 32),
        # E_avg = 20*d^2. The scaling inside the erfc becomes 1/20 = 0.05
        "theory": lambda snr_lin: 1.625 * erfc(np.sqrt(0.05 * snr_lin)) - 0.6875 * (erfc(np.sqrt(0.05 * snr_lin)))**2,
        "snr_range": np.arange(4, 24, 2),
        "pn_list": [0, 2, 5]
    },
    "64-QAM": {
        "gen": lambda n: engine.generate_generic_qam(n, 64),
        "demod": lambda s: engine.demodulate_generic_qam(s, 64),
        "theory": lambda snr_lin: 1.75 * erfc(np.sqrt(snr_lin / 42.0)) - 0.765625 * (erfc(np.sqrt(snr_lin / 42.0)))**2,
        "snr_range": np.arange(8, 26, 2), # 64-QAM needs higher SNR
        "pn_list": [0, 2, 5] # 64-QAM is highly sensitive to phase noise
    },
    "128-QAM": {
        "gen": lambda n: engine.generate_cross_qam(n, 128),
        "demod": lambda s: engine.demodulate_cross_qam(s, 128), # Or engine.demodulate_cross_qam depending on where you saved it
        "theory": lambda snr_lin: 1.8125 * erfc(np.sqrt(snr_lin / 82.0)) - 0.828125 * (erfc(np.sqrt(snr_lin / 82.0)))**2,
        "snr_range": np.arange(12, 32, 2),
        "pn_list": [0, 2, 5] 
    },
    "256-QAM": {
        "gen": lambda n: engine.generate_generic_qam(n, 256),
        "demod": lambda s: engine.demodulate_generic_qam(s, 256),
        "theory": lambda snr_lin: 1.875 * erfc(np.sqrt(snr_lin / 170.0)) - 0.87890625 * (erfc(np.sqrt(snr_lin / 170.0)))**2,
        "snr_range": np.arange(16, 36, 2), # Requires very high SNR to overcome noise
        "pn_list": [0, 2, 5] 
    },
    "64-HQAM": {
        "gen": lambda n: engine.generate_hex_qam(n, 64),
        "demod": lambda s: engine.demodulate_hex_qam(s, 64)[1],
        "theory": lambda snr_lin: 3.5 * erfc(np.sqrt(0.07 * snr_lin)), # Approximation for Hex
        "snr_range": np.arange(10, 28, 2),
        "pn_list": [0, 1, 2]
    },
}

def run_simulation(mod_name, snr_db, pn_std_deg):
    num_symbols = 20000000 # 100k is enough for a smooth curve and much faster
    config = MOD_CONFIG[mod_name]
    
    # 1. Generate tx signal
    tx = config["gen"](num_symbols)
    
    # 2. Apply Impairments
    rx = engine.apply_phase_noise(tx, pn_std_deg)
    rx = engine.apply_awgn(rx, snr_db)
    
    # 3. Demodulate
    if "HQAM" in mod_name or "HQAM" in mod_name:
        m_val = int(mod_name.split('-')[0])
        # Get indices of closest points
        indices, ideal_points = engine.demodulate_hex_qam(rx, m_val)
        # Map those indices back to complex coordinates for comparison
        decoded = ideal_points[indices]
    else:
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
    plot_performance("256-QAM")