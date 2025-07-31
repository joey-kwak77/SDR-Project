import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pynput import keyboard as kb
import threading
import time
                                                               
# Settings
fs = 44100
chunk = 1024                          
bits = 8
levels = 2**bits

talk = threading.Event()
recording_done = threading.Event()

# Buffers
live_buffer = np.zeros(chunk)
recorded_audio = []

# Quantization
def quantize(signal, levels):
    return np.round(signal * (levels // 2 - 1)) / (levels // 2 - 1)

def audio_to_bits(buffer, levels):
    quantized = quantize(buffer, levels)
    int_levels = ((quantized + 1) / 2 * (levels - 1)).astype(int)
    return [format(val, '08b') for val in int_levels]

# Plot setup
fig, ax = plt.subplots()
x = np.arange(chunk)
raw_line, = ax.plot(x, np.zeros(chunk), label="Raw")
quant_line, = ax.plot(x, np.zeros(chunk), linestyle='dashed', label="Quantized")
ax.set_ylim(-1, 1)
ax.set_xlim(0, chunk)
ax.set_title("Live Audio Input")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.legend()

def update_plot(frame):
    raw_line.set_ydata(live_buffer)
    quant_line.set_ydata(quantize(live_buffer, levels))
    return raw_line, quant_line

ani = animation.FuncAnimation(fig, update_plot, interval=10, blit=True)

# Keyboard handlers
def on_press(key):
    if key == kb.Key.space and not talk.is_set():
        print("Recording started...")
        talk.set()

def on_release(key):
    if key == kb.Key.space and talk.is_set():
        print("Recording stopped.")
        talk.clear()
        recording_done.set()
        return False  # stop keyboard listener

# Audio callback
def audio_callback(indata, frames, time, status):
    global live_buffer, recorded_audio
    if status:
        print("Audio Status:", status)
    live_buffer[:] = indata[:, 0]
    if talk.is_set():
        recorded_audio.append(indata.copy())

# Start listener
print("Press and hold SPACE to record. Release to stop.")
listener = kb.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Start audio stream
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=fs, blocksize=chunk)
stream.start()

# Run non-blocking plot loop
while not recording_done.is_set():
    plt.pause(0.01)  # allow GUI updates

# Cleanup
plt.close(fig)
stream.stop()
stream.close()
listener.join()


# Combine and convert audio
if recorded_audio:
    audio_clip = np.concatenate(recorded_audio, axis=0).flatten()
    bit_array = audio_to_bits(audio_clip, levels)

    # Output
    print(f"\nRecorded {len(audio_clip)/fs:.2f} seconds of audio")
    print(f"Total bits captured: {len(bit_array)*bits}")
    print("First 10 audio samples as bits:")
    print(bit_array[:20])
else:
    print("\nNo audio was recorded. Make sure you press and hold the spacebar while the plot window is open.")


# %%
# ------------------------------------------------------------------------------------------------------------------------------------------------

from PAM import Pam
from comms_lib.pluto import Pluto
from comms_lib.system import DigitalCommSystem

# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 10e6  # baseband sampling rate (samples per second)
ts = 1 / fs  # baseband sampling period (seconds per sample)
sps = 5 # samples per second
T = ts * sps  # time between data symbols (seconds per symbol)

# ---------------------------------------------------------------
# Initialize transmitter and receiver.
# ---------------------------------------------------------------
sdr = Pluto("usb:2.9.5")  # change to your Pluto device
tx = sdr
tx.tx_gain = 60  # set the transmitter gain         (power)

rx = tx
# Uncomment the line below to use different Pluto devices for tx and rx
rx.rx_gain = 60  # set the receiver gain

system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)


# %%

'''
convert the bits into a signal to send

8 bits per signal ---> N = 256

Process:
convert bits to symbols (map to constellation of PAM level 256)
convert symbols to message
'''
sps = 3
N = 4 
P = Pam()
symb = P.digital_modulation(bit_array, N)
transmit_signal = P.create_message(symb, sps)


print("Transmit signal length:", len(transmit_signal))
print(type(transmit_signal))
print(transmit_signal)
chunk_size = 50000
num_chunks = int(np.ceil(len(transmit_signal) / chunk_size))
all_received = []

print(f"\nTransmitting {num_chunks} chunks...")
for i in range(num_chunks):
    start = i * chunk_size
    end = min(start + chunk_size, len(transmit_signal))
    chunk = transmit_signal[start:end]

    print(f"Transmitting chunk {i + 1}/{num_chunks} (length = {len(chunk)})")
    system.transmit_signal(chunk)
    time.sleep(0.5)  # Pause to allow complete transmit

    received = system.receive_signal()
    print(f"Received chunk {i + 1} length: {len(received)}")
    all_received.append(received)

receive_signal = np.concatenate(all_received)
print(f"Total received signal length: {len(receive_signal)}")
# system.transmit_signal(transmit_signal)

# receive_signal = system.receive_signal()


plt.figure(figsize=(12, 10))
plt.subplot(2, 1, 1)
plt.plot(np.real(transmit_signal), color="blue", marker="o", label="Real Transmit")
plt.plot(np.real(receive_signal), color="red", label="Real Receive")
plt.title("Transmit and Receive Signals (Real)")
plt.xlabel("Time Samples")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(np.imag(transmit_signal), color="blue", marker="o", label="Imaginary Transmit")
plt.plot(np.imag(receive_signal), color="red", label="Imaginary Receive")
plt.title("Transmit and Receive Signals (Imaginary)")
plt.xlabel("Time Samples")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

plt.show()

# receive_signal = transmit_signal # change later


s = P.decode_message(receive_signal, sps, N)
s = P.detect_pam_symbol(N, s)
b = P.symbol_to_bits(N, s)

print(f"Same signal received? {b == bit_array}")



'''
shift bits to create voice changer effect
convert bits back to audio
apply low pass filter to reduce noise in the audio
'''

def bits_to_audio(bit_array, levels):
    # Convert each 8-bit string back to int
    int_levels = np.array([int(b, 2) for b in bit_array], dtype=np.int32)

    # Map from [0, 255] → [-1, 1] (inverse of quantization step)
    audio = (int_levels / (levels - 1)) * 2 - 1

    return audio.astype(np.float32)



def sinc_lpf(B, fs, num_taps):
    """Return a low-pass filter using a sinc function.
    
    Args:
        B (float): Bandwidth of the filter.
        fs (float): Sampling frequency.
        num_taps (int): Number of taps in the filter."""

    if num_taps % 2 == 0:
        raise ValueError("num_taps must be odd")

    t = np.arange(-num_taps // 2, num_taps // 2 + 1)
    sinc_arg = 2 * cutoff_freq * t / fs
    h = 2 * cutoff_freq / fs * np.sinc(sinc_arg)

    # Normalize the filter coefficients
    h /= np.sum(h)

    return h


def low_pass_filter(data, cutoff_freq, fs, num_taps=101):
    """Implement a low pass filter using a sinc function, where the samping rate is f0

    Args:
        data (np.ndarray): Input signal to be filtered.
        cutoff_freq (float): Cutoff frequency of the low pass filter.

    Returns:
        np.ndarray: Filtered signal.
    """

    #implement the low pass filter using a sinc function
    h = sinc_lpf(cutoff_freq, fs, num_taps)
    return np.convolve(data, h, mode='same')

    


levels = 256  # bits = 8
reconstructed_audio = bits_to_audio(b, levels) 

cutoff_freq = 4000  # for speech, 3–4 kHz is usually sufficient
filtered = low_pass_filter(reconstructed_audio, cutoff_freq=4000, fs=100)


'''
pitch shift
'''
import librosa


# ask the user for the pitch shift step
while True:
  user_input = input("how many steps do you want the pitch to be shifted (ex. 13, -9 etc.): ")
  try:
    n_steps = int(user_input)
    break
  except ValueError:
    print("Invalid input. Please enter an integer number.")


shifted = librosa.effects.pitch_shift(filtered, sr=44100, n_steps=n_steps)

         
# Playback the audio
print("Playing recieved audio...")
sd.play(shifted, samplerate=44100)
sd.wait()

