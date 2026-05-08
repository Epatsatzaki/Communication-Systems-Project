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
    
def generate_hex_qam(num_symbols, m):
    """Generates a rectangular box-shaped Hexagonal QAM constellation."""
    n = int(np.sqrt(m)) # 4 for 16, 8 for 64
    points = []
    
    for row in range(n):
        for col in range(n):
            # x is shifted by 0.5 for odd rows
            x = col + 0.5 * (row % 2)
            y = row * (np.sqrt(3) / 2)
            points.append(x + 1j * y)
            
    points = np.array(points)
    
    # Center the constellation around (0,0)
    points -= np.mean(points)
    
    # Map and Normalize
    data = np.random.choice(points, num_symbols)
    norm = np.sqrt(np.mean(np.abs(points)**2))
    return data / norm

def demodulate_hex_qam(received_sig, m):
    """
    Demodulates Hexagonal QAM using Minimum Euclidean Distance.
    """
    # 1. Recreate the EXACT ideal constellation used during generation
    # (Must be normalized the same way as the transmitter)
    n = int(np.sqrt(m))
    ideal_points = []
    for row in range(n):
        for col in range(n):
            x = col + 0.5 * (row % 2)
            y = row * (np.sqrt(3) / 2)
            ideal_points.append(x + 1j * y)
            
    ideal_points = np.array(ideal_points)
    ideal_points -= np.mean(ideal_points)
    norm = np.sqrt(np.mean(np.abs(ideal_points)**2))
    ideal_points /= norm # This is our "Codebook"

    # 2. Nearest Neighbor Search
    demodulated_indices = []
    for rx_sym in received_sig:
        # Calculate distance from this received dot to all 16/64 ideal points
        distances = np.abs(rx_sym - ideal_points)
        # Pick the index of the closest ideal point
        best_match_idx = np.argmin(distances)
        demodulated_indices.append(best_match_idx)
        
    return np.array(demodulated_indices), ideal_points

def generate_ask(num_symbols, m):
    # Points at -7, -5, -3, -1, 1, 3, 5, 7 for 8-ASK
    levels = np.arange(-(m-1), m, 2)
    sig = np.random.choice(levels, num_symbols).astype(complex)
    return sig / np.sqrt(np.mean(np.abs(levels)**2))

def generate_apsk(num_symbols, m):
    if m == 16:
        n_rings = [4, 12]
        radii = [1.0, 2.6]
        offsets = [np.pi/4, np.pi/12] 
    elif m == 32:
        n_rings = [4, 12, 16]
        radii = [1.0, 2.54, 4.54]
        offsets = [np.pi/4, np.pi/12, np.pi/16]
    elif m == 64:
        # Standard 64-APSK configuration (e.g., DVB-S2X)
        n_rings = [4, 12, 20, 28]
        radii = [1.0, 2.4, 4.3, 7.0]
        offsets = [np.pi/4, np.pi/12, np.pi/20, np.pi/28]
    elif m == 128:
        # Approximate rings for 128-APSK
        n_rings = [4, 12, 20, 28, 64]
        radii = [1.0, 2.4, 4.3, 7.0, 10.5]
        offsets = [np.pi/4, np.pi/12, np.pi/20, np.pi/28, 0]
    else:
        # Fallback to a circular 16-APSK if m is unrecognized
        n_rings = [4, 12]
        radii = [1.0, 2.6]
        offsets = [np.pi/4, np.pi/12]
    
    points = []
    for n, r, phi in zip(n_rings, radii, offsets):
        # Apply the phi offset here
        angles = np.linspace(0, 2*np.pi, n, endpoint=False) + phi
        points.extend(r * np.exp(1j * angles))
    
    points = np.array(points)
    # Standard normalization logic
    sig = np.random.choice(points, num_symbols)
    return sig / np.sqrt(np.mean(np.abs(points)**2))