import time as os_time
import sounddevice as sd
import numpy as np
from sounddevice import CallbackFlags


def audio_callback(
    indata: np.ndarray, frames: int, time, status: CallbackFlags, sample_rate: int
):
    if status:
        print(status)

    # Perform frequency analysis using FFT
    frequencies = np.fft.fft(indata)

    # Calculate magnitude spectrum
    magnitude_spectrum = np.abs(frequencies)

    # Extract dominant frequency
    # Define frequency range
    freq_min = 250  # Minimum frequency in Hz
    freq_max = 1000  # Maximum frequency in Hz

    # Find indices corresponding to frequency range
    freq_bins = np.fft.fftfreq(len(indata)) * sample_rate
    min_idx = np.argmax(freq_bins > freq_min)
    max_idx = np.argmax(freq_bins > freq_max)

    # Calculate intensity of sound between frequencies
    intensity = np.sum(magnitude_spectrum[min_idx:max_idx])

    # Create numpy array with timestamp and intensity
    # data_point = np.array([timestamp, intensity])
    print(f"Frames: {os_time.time()}", f"{int(intensity * 100) * '#'}")


def process_stream(chunk_duration, sample_rate, callback):
    try:
        while True:
            with sd.InputStream(
                channels=1,
                callback=callback,
                samplerate=sample_rate,
            ):
                print(f"Streaming audio for {chunk_duration} seconds...")
                sd.sleep(int(chunk_duration * 1000))
    except KeyboardInterrupt:
        print("Stopping audio stream.")
