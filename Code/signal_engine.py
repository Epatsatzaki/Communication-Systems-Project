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

def generate_generic_qam(num_symbols, m):
    """Generates M-QAM symbols (M must be a square number like 64, 256)."""
    n = int(np.sqrt(m))
    data = np.random.randint(0, m, num_symbols)
    i = 2 * (data // n) - (n - 1)
    q = 2 * (data % n) - (n - 1)
    
    # Normalization: Average power for M-QAM is (M-1)/3
    norm = np.sqrt((m - 1) / 3.0)
    return (i + 1j * q) / norm

def generate_cross_qam(num_symbols, m):
    """Generates 32-QAM or 128-QAM cross constellations."""
    # Determine the grid size (6x6 for 32, 12x12 for 128)
    if m == 32:
        n, corners = 6, 1 # Remove 1 point from each corner of the 6x6 grid
    elif m == 128:
        n, corners = 12, 2 # Remove 4 points (2x2) from each corner of the 12x12 grid
    else:
        raise ValueError("This function is specifically for 32 or 128 cross-QAM.")

    # Create the grid
    points = []
    limit = n - 1
    for i in range(-limit, limit + 1, 2):
        for q in range(-limit, limit + 1, 2):
            # Check if the point is in the corner 'exclusion zone'
            if not (abs(i) > (limit - 2*corners) and abs(q) > (limit - 2*corners)):
                points.append(i + 1j * q)
    
    # Randomly sample from the valid points
    points = np.array(points)
    data = np.random.choice(points, num_symbols)
    
    # Normalization (E_avg is 20 for 32-QAM, ~82 for 128-QAM)
    norm = np.sqrt(np.mean(np.abs(points)**2))
    return data / norm

def demodulate_generic_qam(symbols, m):
    n = int(np.sqrt(m))
    norm = np.sqrt((m - 1) / 3.0)
    scaled = symbols * norm
    
    # Snap to nearest odd integer
    i_hat = 2 * np.round((np.real(scaled) - (-(n-1))) / 2) + (-(n-1))
    q_hat = 2 * np.round((np.imag(scaled) - (-(n-1))) / 2) + (-(n-1))
    
    # Clip boundaries
    limit = n - 1
    i_hat = np.clip(i_hat, -limit, limit)
    q_hat = np.clip(q_hat, -limit, limit)
    
    return (i_hat + 1j * q_hat) / norm