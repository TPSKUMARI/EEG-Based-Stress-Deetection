import numpy as np
import time
import threading
import serial  # Added for serial communication with Arduino

LEFT_EAR_PIN = 4  # GPIO4 (D2 on ESP32)
RIGHT_EAR_PIN = 2  # GPIO2 (D4 on ESP32)
samples = 64  # Number of samples
sampling_frequency = 50  # Hz
sampling_period_us = int(round(1000000 * (1.0 / sampling_frequency)))
noise_threshold = 10.0  # Adjust based on your noise level

def calibrate_baseline():
    calibration_samples = 100
    left_sum = 0
    right_sum = 0
    for _ in range(calibration_samples):
        left_sum += analog_read(LEFT_EAR_PIN)
        right_sum += analog_read(RIGHT_EAR_PIN)
        time.sleep(0.01)  # delay 10ms
    baseline_left = left_sum / calibration_samples
    baseline_right = right_sum / calibration_samples
    v_real_left = np.full(samples, baseline_left - 512.0)
    v_real_right = np.full(samples, baseline_right - 512.0)
    return v_real_left, v_real_right

def analog_read(pin):
    # Replace this with your own implementation to read from analog pin in Python
    # For example, you can use libraries like RPi.GPIO or adafruit_blinka
    # Here, I'll just return a random value for demonstration purposes
    return np.random.randint(0, 1024)

def compute_fft(v_real, v_imag):
    windowed_data = v_real * np.hamming(samples)
    fft_result = np.fft.fft(windowed_data)
    magnitudes = np.abs(fft_result)
    return magnitudes

def calculate_power_in_frequency_bands(magnitudes):
    alpha_power = 0
    beta_power = 0
    for i in range(samples // 2):
        frequency = i * (sampling_frequency / samples)
        if 8 <= frequency <= 12:
            alpha_power += magnitudes[i] ** 2
        elif 13 <= frequency <= 30:
            beta_power += magnitudes[i] ** 2
    return alpha_power, beta_power

def calculate_attention(alpha_power, beta_power):
    attention = beta_power / alpha_power if alpha_power > 0 else 0
    return attention

def stream_eeg():
    while True:
        v_real_left, v_real_right = calibrate_baseline()

        # SAMPLING
        for i in range(samples):
            v_real_left[i] = analog_read(LEFT_EAR_PIN) - 512.0
            v_real_right[i] = analog_read(RIGHT_EAR_PIN) - 512.0
            time.sleep(sampling_period_us / 1000000)  # convert to seconds

        # PROCESSING
        magnitudes_left = compute_fft(v_real_left, np.zeros(samples))
        magnitudes_right = compute_fft(v_real_right, np.zeros(samples))

        # CALCULATE POWER IN FREQUENCY BANDS
        alpha_power_left, beta_power_left = calculate_power_in_frequency_bands(magnitudes_left)
        alpha_power_right, beta_power_right = calculate_power_in_frequency_bands(magnitudes_right)

        # CALCULATE ATTENTION/FOCUS LEVEL
        attention_left = calculate_attention(alpha_power_left, beta_power_left)
        attention_right = calculate_attention(alpha_power_right, beta_power_right)

        # PRINT RESULTS
        print(f"Attention_Left: {attention_left:.2f}\tAttention_Right: {attention_right:.2f}")

        time.sleep(2)  # Repeat after delay

if __name__ == "__main__":
    # Start streaming EEG data
    stream_thread = threading.Thread(target=stream_eeg)
    stream_thread.start()
