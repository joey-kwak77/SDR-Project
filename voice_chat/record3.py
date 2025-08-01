import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pynput import keyboard as kb
import threading
import time
import librosa
from PAM import Pam
from comms_lib.pluto import Pluto
from comms_lib.system import DigitalCommSystem

from comms_lib.dsp import *

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
        return False  

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
    plt.pause(0.01)  

# Cleanup
plt.close(fig)
stream.stop()
stream.close()
listener.join()


# Combine and convert audio
if recorded_audio:
    audio_clip = np.concatenate(recorded_audio, axis=0).flatten()
    bit_strs = audio_to_bits(audio_clip, levels)
    bit_array = np.array([int(b) for bits in bit_strs for b in bits], dtype=int)
    print("Length of bit array: ", len(bit_array))
    # Output
    print(f"\nRecorded {len(audio_clip)/fs:.2f} seconds of audio")
    print(f"Total bits captured: {len(bit_array)*bits}")
    print("First 10 audio samples as bits:")
    print(bit_array[:20])
else:
    print("\nNo audio was recorded. Make sure you press and hold the spacebar while the plot window is open.")



# %%
# ------------------------------------------------------------------------------------------------------------------------------------------------
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
sdr = Pluto("usb:2.7.5")  # change to your Pluto device
tx = sdr
# tx.tx_gain = 90  # set the transmitter gain         (power)

rx = tx
# rx.rx_gain = 40
# Uncomment the line below to use different Pluto devices for tx and rx
# rx.rx_gain = 60  # set the receiver gain
# sdr.carrier_frequency=840e6                       
system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)
system.set_carrier_frequency(870e6)
system.transmitter.tx_gain = 90
system.receiver.rx_gain = 30
system.receiver.rx_buffer_size = int(1e6)

print(system.transmitter)
print(system.receiver)

# K = 24000  # Number of bits
# bit_array = np.random.randint(0, 2, size=K)

# %%

'''
convert the bits into a signal to send

8 bits per signal ---> N = 256

Process:
convert bits to symbols (map to constellation of PAM level 256)
convert symbols to message
'''
sps = 3
N = 16
P = Pam()
# symb = P.digital_modulation(bit_array, N)
# symb = np.asarray(symb)  # Ensure it's a NumPy array
# print(len(symb))

constellation = get_qam_constellation(M=N)
symb, padding = qam_mapper(bit_array,constellation)

perm = np.random.permutation(len(symb))
shuffled_symbol = symb[perm]
transmit_signal = P.create_message(symb, sps)

print("Transmit signal length:", len(transmit_signal))
print(type(transmit_signal))
print(transmit_signal)
chunk_size = 8000
num_chunks = int(np.ceil(len(transmit_signal) / chunk_size))
all_received = []

print(f"\nTransmitting {num_chunks} chunks...")
for i in range(num_chunks):
    start = i * chunk_size
    end = min(start + chunk_size, len(transmit_signal))
    chunk = transmit_signal[start:end]

    print(f"Transmitting chunk {i + 1}/{num_chunks} (length = {len(chunk)})")
    system.transmit_signal(chunk)
    time.sleep(0.5)  

    received = system.receive_signal()
    print(f"Received chunk {i + 1} length: {len(received)}")
    all_received.append(received)

    plt.figure(figsize=(12, 10))
    plt.subplot(2, 1, 1)
    plt.plot(np.real(chunk), color="blue", marker="o", label="Real Transmit")
    plt.plot(np.real(received), color="red", label="Real Receive")
    plt.title("Transmit and Receive Signals (Real)")
    plt.xlabel("Time Samples")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()
    plt.show()

receive_signal = np.concatenate(all_received)
print(f"Total received signal length: {len(receive_signal)}")

plt.figure(figsize=(12, 10))
plt.subplot(2, 1, 1)
plt.plot(np.real(transmit_signal), color="blue", marker="o", label="Real Transmit")
plt.plot(np.real(receive_signal), color="red", label="Real Receive")
plt.title("Transmit and Receive Signals (Real)")
plt.xlabel("Time Samples")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

# s = P.decode_message(receive_signal, sps, N)
# s_orig = s
# s = P.detect_pam_symbol(N, s)
# s = np.asarray(s)

rx_symbols = receive_signal[sps//2::sps]
rx_symb = demod_nearest(rx_symbols, constellation)

#unperm = np.argsort(perm)
#unshuffled_symbols = s[unperm]
#b = P.symbol_to_bits(N, s)

unperm = np.argsort(perm)
rx_symb = rx_symb[unperm]

rx_bit_array = qam_demapper(rx_symb,padding,constellation)

b = rx_bit_array

print(f"Same signal received? {b == bit_array}")

tx_symbols = np.asarray(symb)

plt.figure(figsize=(8, 8))
plt.scatter(rx_symbols.real, rx_symbols.imag, color='red', marker='x', label='Received', alpha=0.6)
plt.scatter(tx_symbols.real, tx_symbols.imag, color='blue', marker='o', label='Transmitted', alpha=0.6)
plt.title('Transmitted vs Received Constellation')
plt.xlabel('In-Phase (I)')
plt.ylabel('Quadrature (Q)')
plt.grid(True)
plt.axis('equal')
plt.legend()
plt.show()


'''
convert bits back to audio
apply low pass filter to reduce noise in the audio
'''

def bits_to_audio(bit_array, levels):
    # Convert each 8-bit string back to int
    
    int_levels = np.array([int(b, 2) for b in bit_array], dtype=np.int32)

    # Map from [0, 255] → [-1, 1] (inverse of quantization step)
    audio = (int_levels / (levels - 1)) * 2 - 1

    return audio.astype(np.float32)


levels = 256  # bits = 8

bit_strs = [''.join(str(bit) for bit in b[i:i+8]) for i in range(0, len(b), 8)]
reconstructed_audio = bits_to_audio(bit_strs, levels) 


'''
pitch shift
'''


# ask the user for the pitch shift step
while True:
  user_input = input("how many steps do you want the pitch to be shifted (ex. 13, -9 etc.): ")
  try:
    n_steps = int(user_input)
    break
  except ValueError:
    print("Invalid input. Please enter an integer number.")


shifted = librosa.effects.pitch_shift(reconstructed_audio, sr=44100, n_steps=n_steps)

         
# playback the audio
print("Playing recieved audio...")
sd.play(shifted, samplerate=44100)
sd.wait()

