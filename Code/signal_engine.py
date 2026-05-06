import numpy as np

# --- IMPAIRMENT MODELS ---

def apply_awgn(symbols, snr_db):
    snr_linear = 10**(snr_db / 10.0)
    noise_std = np.sqrt(1 / (2 * snr_linear))
    return symbols + noise_std * (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols)))

def apply_phase_noise(symbols, std_deg):
    std_rad = np.deg2rad(std_deg)
    noise_phase = np.random.normal(0, std_rad, len(symbols))
    return symbols * np.exp(1j * noise_phase)

def apply_iq_imbalance(symbols, amp_db, phase_deg):
    g = 10**(amp_db / 20.0) 
    phi = np.deg2rad(phase_deg)
    i, q = np.real(symbols), np.imag(symbols)
    i_imb = g * i * np.cos(phi/2) - g * q * np.sin(phi/2)
    q_imb = (1/g) * q * np.cos(phi/2) - (1/g) * i * np.sin(phi/2)
    return i_imb + 1j * q_imb

def apply_jamming(symbols, jamming_power_db):
    jam_p_lin = 10**(jamming_power_db / 10.0)
    phase = np.linspace(0, 2*np.pi, len(symbols))
    return symbols + np.sqrt(jam_p_lin) * np.exp(1j * phase)

def apply_amplitude_distortion(symbols, nl_factor):
    mag = np.abs(symbols)
    distorted_mag = mag / (1 + nl_factor * mag)
    return distorted_mag * np.exp(1j * np.angle(symbols))

# --- GENERATION FUNCTIONS ---

def generate_qpsk(num_symbols):
    bits = np.random.randint(0, 2, (num_symbols, 2))
    symbols = (2 * bits[:, 0] - 1) + 1j * (2 * bits[:, 1] - 1)
    return symbols / np.sqrt(2)

def generate_16qam(num_symbols):
    data = np.random.randint(0, 16, num_symbols)
    i = 2 * (data // 4) - 3
    q = 2 * (data % 4) - 3
    return (i + 1j * q) / np.sqrt(10)


def demodulate_16qam(symbols):
    """Hard decision demodulator for normalized 16-QAM."""
    # 1. Scale back from unit power to the integer grid [-3, -1, 1, 3]
    # We use sqrt(10) because E_s for 16-QAM is 10
    scaled = symbols * np.sqrt(10)
    
    # 2. Map to the nearest odd integer (-3, -1, 1, 3)
    # This is the "Decision Rule" for QAM
    i_hat = 2 * np.round((np.real(scaled) - 1) / 2) + 1
    q_hat = 2 * np.round((np.imag(scaled) - 1) / 2) + 1
    
    # 3. Boundary Clipping (keeps points inside the 4x4 grid)
    i_hat = np.clip(i_hat, -3, 3)
    q_hat = np.clip(q_hat, -3, 3)
    
    # 4. Normalize back so we can compare with the original tx symbols
    return (i_hat + 1j * q_hat) / np.sqrt(10)


# Add 64-QAM, BPSK, 8-ASK, etc. here as you go!