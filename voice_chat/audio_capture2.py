import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pynput import keyboard as kb
import threading

# Settings
fs = 44100          # Sample rate
chunk = 1024       # Samples per frame
bits = 8            # Bits for ADC
levels = 2**bits    # Quantization levels

talk  = threading.Event()            # True while space is held


# Create figure for plotting
fig, ax = plt.subplots()
x = np.arange(0, chunk)
raw_line, = ax.plot(x, np.zeros(chunk), label="Raw")
quant_line, = ax.plot(x, np.zeros(chunk), label="Quantized", linestyle='dashed')
ax.set_ylim(-1, 1)
ax.set_xlim(0, chunk)
ax.set_title("Live Mic Input")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.legend()

# Shared buffer for animation
buffer = np.zeros(chunk)

# ADC Quantization
def quantize(signal, levels):
    return np.round(signal * (levels // 2 - 1)) / (levels // 2 - 1)

# keyboard handlers (UI thread)
def on_press(key):
    if key == kb.Key.space:
        if not talk.is_set():
            talk.set()

def on_release(key):
    if key == kb.Key.space:
        if talk.is_set():
            talk.clear()

# Start keyboard listener explicitly in its own thread
listener = kb.Listener(on_press=on_press, on_release=on_release)
listener.start()


# Callback: fills buffer with live input
def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    if talk.is_set():            # mute unless space pressed
        buffer = indata[:, 0]
    else:
        buffer[:] = 0


    bit_strs = audio_to_bits(buffer, levels,10)
    print("Bits:", ' '.join(bit_strs[:10]))

# Update the animation frame
def update_plot(frame):
    raw_line.set_ydata(buffer)
    quant_line.set_ydata(quantize(buffer, levels))

    # Don't transmit if muted (buffer is all zeros)
    if not np.any(buffer):  # True if all elements are 0 (i.e., silence)
        return raw_line, quant_line
 
    return raw_line, quant_line

def audio_to_bits(buffer, levels, num_samples):
    # Quantize
    quantized = quantize(buffer, levels)

    # Convert to integer (0–255)
    int_levels = ((quantized + 1) / 2 * (levels - 1)).astype(int)

    # Convert to bits (only print first 20 samples)
    bit_strings = []
    for val in int_levels[:num_samples]:
        bit_str = format(val, '08b')  # Convert integer to 8-bit binary string
        bit_strings.append(bit_str)    
    

    return bit_strings


# Start stream
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=fs, blocksize=chunk)
ani = animation.FuncAnimation(fig, update_plot, interval=10)

with stream:
    plt.show()

