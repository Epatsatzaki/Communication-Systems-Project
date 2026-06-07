import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import signal_engine as engine 

# --- HELPER FUNCTION: Phase Noise Conversion ---
def dbchz_to_degrees(pn_dbc_hz, symbol_rate):
    """
    Converts a flat phase noise density (dBc/Hz) into baseband 
    phase error standard deviation (degrees) for a given symbol rate.
    """
    if pn_dbc_hz == "-inf" or pn_dbc_hz == 0:  # Handle the ideal case (no phase noise)
        return 0.0
        
    # Convert dBc/Hz to linear power density
    linear_density = 10**(pn_dbc_hz / 10.0)
    
    # Integrate over the double-sided Nyquist bandwidth
    variance_rad = linear_density * symbol_rate
    
    # Calculate standard deviation in radians, then convert to degrees
    std_dev_rad = np.sqrt(variance_rad)
    std_dev_deg = std_dev_rad * (180.0 / np.pi)
    
    return std_dev_deg

# --- CONFIGURATION DICTIONARY ---
# Each entry contains: Generation function, Demodulation logic, Exact Theory, and dBc/Hz arrays
MOD_CONFIG = {
    "QPSK": {
        "gen": engine.generate_qpsk,
        "demod": lambda syms: (np.sign(np.real(syms)) + 1j * np.sign(np.imag(syms))) / np.sqrt(2),
        "theory": lambda snr_lin: erfc(np.sqrt(snr_lin / 2)) - 0.25 * (erfc(np.sqrt(snr_lin / 2)))**2,
        "snr_range": np.arange(0, 16, 2),
        "pn_list": ["-inf", -89, -81] # dBc/Hz (Ideal, Moderate, Severe)
    },
    "16-QAM": {
        "gen": lambda n: engine.generate_generic_qam(n, 16),
        "demod": lambda s: engine.demodulate_generic_qam(s, 16),
        "theory": lambda snr_lin: 1.5 * erfc(np.sqrt(0.1 * snr_lin)) - 0.5625 * (erfc(np.sqrt(0.1 * snr_lin)))**2,
        "snr_range": np.arange(0, 22, 2),
        "pn_list": ["-inf", -89, -81]  # 16-QAM requires cleaner oscillators
    },
    "32-QAM": {
        "gen": lambda n: engine.generate_cross_qam(n, 32),
        "demod": lambda s: engine.demodulate_cross_qam(s, 32),
        "theory": lambda snr_lin: 1.625 * erfc(np.sqrt(0.05 * snr_lin)) - 0.6875 * (erfc(np.sqrt(0.05 * snr_lin)))**2,
        "snr_range": np.arange(4, 24, 2),
        "pn_list": ["-inf", -89, -81] 
    },
    "64-QAM": {
        "gen": lambda n: engine.generate_generic_qam(n, 64),
        "demod": lambda s: engine.demodulate_generic_qam(s, 64),
        "theory": lambda snr_lin: 1.75 * erfc(np.sqrt(snr_lin / 42.0)) - 0.765625 * (erfc(np.sqrt(snr_lin / 42.0)))**2,
        "snr_range": np.arange(8, 26, 2), 
        "pn_list": ["-inf", -89, -81] 
    },
    "128-QAM": {
        "gen": lambda n: engine.generate_cross_qam(n, 128),
        "demod": lambda s: engine.demodulate_cross_qam(s, 128), 
        "theory": lambda snr_lin: 1.8125 * erfc(np.sqrt(snr_lin / 82.0)) - 0.828125 * (erfc(np.sqrt(snr_lin / 82.0)))**2,
        "snr_range": np.arange(12, 32, 2),
        "pn_list": ["-inf", -89, -81] 
    },
    "256-QAM": {
        "gen": lambda n: engine.generate_generic_qam(n, 256),
        "demod": lambda s: engine.demodulate_generic_qam(s, 256),
        "theory": lambda snr_lin: 1.875 * erfc(np.sqrt(snr_lin / 170.0)) - 0.87890625 * (erfc(np.sqrt(snr_lin / 170.0)))**2,
        "snr_range": np.arange(16, 36, 2), 
        "pn_list": ["-inf", -89, -81] 
    },
    "64-HQAM": {
        "gen": lambda n: engine.generate_hex_qam(n, 64),
        "demod": lambda s: engine.demodulate_hex_qam(s, 64)[1],
        "theory": lambda snr_lin: 3.5 * erfc(np.sqrt(0.07 * snr_lin)), 
        "snr_range": np.arange(10, 28, 2),
        "pn_list": ["-inf", -105, -95]
    },
}

def run_simulation(mod_name, snr_db, pn_dbc_hz, symbol_rate=1e6):
    num_symbols = 200000 # Keep at 200k for standard testing; push to 20M for final high-SNR runs
    config = MOD_CONFIG[mod_name]
    
    # 1. Convert RF dBc/Hz to baseband degrees
    pn_std_deg = dbchz_to_degrees(pn_dbc_hz, symbol_rate)
    
    # 2. Generate tx signal
    tx = config["gen"](num_symbols)
    
    # 3. Apply Impairments
    rx = engine.apply_phase_noise(tx, pn_std_deg)
    rx = engine.apply_awgn(rx, snr_db)
    
    # 4. Demodulate
    if "HQAM" in mod_name:
        m_val = int(mod_name.split('-')[0])
        indices, ideal_points = engine.demodulate_hex_qam(rx, m_val)
        decoded = ideal_points[indices]
    else:
        decoded = config["demod"](rx)
    
    # 5. Count Errors
    errors = np.sum(np.abs(tx - decoded) > 0.01)
    return errors / num_symbols

def plot_performance(mod_name, symbol_rate=1e6):
    config = MOD_CONFIG[mod_name]
    snr_range = config["snr_range"]
    
    plt.figure(figsize=(10, 7))
    
    # Theoretical Baseline
    snr_lin_fine = 10**(np.linspace(snr_range[0], snr_range[-1], 100) / 10.0)
    plt.semilogy(np.linspace(snr_range[0], snr_range[-1], 100), 
                 config["theory"](snr_lin_fine), 'k--', label=f'Theoretical {mod_name}')
    
    # Simulation Loops
    for pn in config["pn_list"]:
        label_str = f'Simulated PN = {pn} dBc/Hz' if pn != "-inf" else 'Simulated Ideal (No PN)'
        print(f"Simulating {mod_name} | Phase Noise: {pn} dBc/Hz...")
        
        sep_results = [run_simulation(mod_name, snr, pn, symbol_rate) for snr in snr_range]
        plt.semilogy(snr_range, sep_results, 'o-', label=label_str)

    plt.grid(True, which='both')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Symbol Error Probability (SEP)')
    plt.title(f'{mod_name} SEP vs SNR in Presence of Phase Noise (Rs = {symbol_rate/1e6} MHz)')
    plt.legend()
    plt.ylim([1e-5, 1])
    plt.show()

if __name__ == "__main__":
    # Just change this string to switch the whole script!
    plot_performance("16-QAM", symbol_rate=1e6)