import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pynput import keyboard as kb
import threading


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

# Quantization function
def quantize(signal, levels):
    return np.round(signal * (levels // 2 - 1)) / (levels // 2 - 1)

# Audio-to-bits
def audio_to_bits(buffer, levels):
    quantized = quantize(buffer, levels)
    int_levels = ((quantized + 1) / 2 * (levels - 1)).astype(int)
    return [format(val, '08b') for val in int_levels]

# Keyboard events
def on_press(key):
    if key == kb.Key.space and not talk.is_set():
        print("Recording started...")
        talk.set()

def on_release(key):
    if key == kb.Key.space and talk.is_set():
        print("Recording stopped.")
        talk.clear()
        recording_done.set()
        return False  # stop listener

# Audio callback
def audio_callback(indata, frames, time, status):
    global live_buffer, recorded_audio
    if status:
        print("Audio Status:", status)

    live_buffer[:] = indata[:, 0]

    if talk.is_set():
        recorded_audio.append(indata.copy())

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

# Animation update
def update_plot(frame):
    raw_line.set_ydata(live_buffer)
    quant_line.set_ydata(quantize(live_buffer, levels))
    return raw_line, quant_line

ani = animation.FuncAnimation(fig, update_plot, interval=10, blit=True)

# Start keyboard listener
print("Press and hold SPACE to record. Release to stop.")
listener = kb.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Start stream and plot
with sd.InputStream(callback=audio_callback, channels=1, samplerate=fs, blocksize=chunk):
    plt.show()  # blocks until window closed

# Wait for recording to finish (keyboard release)
recording_done.wait()

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


# %%
# ------------------------------------------------------------------------------------------------------------------------------------------------

from PAM import Pam
from comms_lib.pluto import Pluto
from comms_lib.system import DigitalCommSystem

'''
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
sdr = Pluto("usb:1.1.5")  # change to your Pluto device
tx = sdr
tx.tx_gain = 90  # set the transmitter gain         (power)

rx = tx
# Uncomment the line below to use different Pluto devices for tx and rx
rx.rx_gain = 90  # set the receiver gain
'''
system = DigitalCommSystem()
# system.set_transmitter(tx)
# system.set_receiver(rx)


# %%

'''
convert the bits into a signal to send

8 bits per signal ---> N = 256

Process:
convert bits to symbols (map to constellation of PAM level 256)
convert symbols to message
'''
sps = 5
N = 16
P = Pam()
symb = P.digital_modulation(bit_array, 256)
transmit_signal = P.create_message(symb, sps)


'''
send the message over Pluto and decode

Process:
transmit and recieve message
decode message to symbols
correct transmitted symbols
convert symbols back to bits
'''

# sdr stuff ew


'''
# Pluto stuff
sdr.tx(m)

rx_signal = sdr.rx()  # Capture raw samples from Pluto

'''
# system.transmit_signal(transmit_signal)

# receive_signal = system.receive_signal()

receive_signal = (
    transmit_signal
    + np.random.normal(0, 0.1, transmit_signal.shape)
    + 1j * np.random.normal(0, 0.1, transmit_signal.shape)
)


s = P.decode_message(receive_signal, sps, N)
s = P.detect_pam_symbol(N, s)
b = P.symbol_to_bits(N, s)

print(b == bit_array)



'''
shift bits to create voice changer effect
convert bits back to audio
'''

