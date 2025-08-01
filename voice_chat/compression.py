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
    print(bit_array[:10])
else:
    print("\nNo audio was recorded. Make sure you press and hold the spacebar while the plot window is open.")


# ------------------------------------------------------------------------------------------------------------------------------------------------
# compression and decompression

"""
Compress bit_array using differential encoding !
"""
                           
def compression(b: np.array) -> str:
    '''
    compress the bits using differential encoding
    Return:
        encoded: a string of bits
            first 8: starting value
            after: 4 bit values --> [0]: +/-, [1:]: diff in binary 
    '''
    # bits = [b[i:i + 8] for i in range(0, b.size, 8)]
    bits = b

    encoded = bits[0]
    prev = int(bits[0], 2)

    for b in bits[1:]:              
        diff = (int(b, 2) - prev)

        if (abs(diff) > 8):
            diff = max(-8, min(8, diff))

        if (diff < 0):
            encoded += ("0" + str(f'{(abs(diff)):03b}'))
        else:
            encoded += ("1" + str(f'{(diff):03b}'))

        prev = (prev + diff) & 0xFF

    return encoded


def decompression(encoded):
    '''
    decompress numpy array back into original bit_array form
    '''
    # bit_str = "".join(encoded.astype(str))
    bit_str = str(encoded)
    nBits = 4
    res = []

    # get first value:
    res.append(bit_str[:8])
    prev = int(bit_str[:8], 2)

    bit_str = bit_str[8:]

    for i in range(0, len(bit_str), nBits):
        sign = bit_str[i]
        diff = bit_str[i+1:i+nBits]

        if (diff == ""):
            break

        diff = int(diff, 2)

        if sign == "0": # neg
            res.append(f'{(prev - diff):08b}')
            prev -= diff
        else:
            res.append(f'{(prev + diff):08b}')
            prev += diff
    return res



compressed = compression(bit_array)
print("Length of compressed data: " + str(len(compressed)))
# print("compressed data: " + compressed[:100])


# Corrept the symbols
n = np.fromiter(compressed, dtype='U1')
n = n.astype(int)
corrupt = (
    n
    + np.random.normal(0, 0.1, n.shape)
    + 1j * np.random.normal(0, 0.1, n.shape)
)
c = "".join(corrupt.astype(str))



decomp = decompression(c)
print(decomp[:10])
print("Data lost: " + str(not(decomp == bit_array)))



def bits_to_audio(bit_array, levels):
    # Convert each 8-bit string back to int
    int_levels = np.array([int(b, 2) for b in bit_array], dtype=np.int32)

    # Map from [0, 255] → [-1, 1] (inverse of quantization step)
    audio = (int_levels / (levels - 1)) * 2 - 1

    return audio.astype(np.float32)

reconstructed_audio = bits_to_audio(decomp, 256) 

# Playback the audio
print("Playing recieved audio...")
sd.play(reconstructed_audio, samplerate=44100)
sd.wait()


