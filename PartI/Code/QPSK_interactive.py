import matplotlib.pyplot as plt
from signal_engine import * # Assuming the file above is named signal_engine.py

def main():
    print("--- QPSK Impairment Simulator ---")
    snr = float(input("Enter SNR (dB): "))
    p_noise = float(input("Enter Phase Noise (std dev in degrees): "))
    iq_amp = float(input("Enter I/Q Amp Imbalance (dB, e.g. 0.5): "))
    iq_phi = float(input("Enter I/Q Phase Imbalance (degrees): "))

    # 1. Generate
    tx_symbols = generate_qpsk(1000)
    
    # 2. Add Impairments
    rx_symbols = apply_phase_noise(tx_symbols, p_noise)
    rx_symbols = apply_iq_imbalance(rx_symbols, iq_amp, iq_phi)
    rx_symbols = apply_awgn(rx_symbols, snr)

    # 3. Plot
    plt.figure(figsize=(6,6))
    plt.scatter(np.real(rx_symbols), np.imag(rx_symbols), s=1, alpha=0.6)
    plt.axhline(0, color='black', lw=1)
    plt.axvline(0, color='black', lw=1)
    plt.title(f"QPSK: SNR={snr}dB, PN={p_noise}°, IQ_imb={iq_amp}dB/{iq_phi}°")
    plt.grid(True)
    plt.xlim([-2, 2])
    plt.ylim([-2, 2])
    plt.show()

if __name__ == "__main__":
    main()