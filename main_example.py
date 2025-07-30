# %%
# ruff: noqa: F405
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from comms_lib.pluto import Pluto
from comms_lib.system import DigitalCommSystem

# %%
# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 10e6  # baseband sampling rate (samples per second)
ts = 1 / fs  # baseband sampling period (seconds per sample)
sps = 3
T = ts * sps  # time between data symbols (seconds per symbol)

# ---------------------------------------------------------------
# Initialize transmitter and receiver.
# ---------------------------------------------------------------
tx = Pluto("usb:2.10.5")  # change to your Pluto device
tx.tx_gain = 90  # set the transmitter gain

rx = tx
# Uncomment the line below to use different Pluto devices for tx and rx
# rx = Pluto("usb:7.6.5")
# rx.rx_gain = 90  # set the receiver gain

# %%
# ---------------------------------------------------------------
# Initialize digital communication system and define system parameters.
# ---------------------------------------------------------------
system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)

# TODO: generate your own transmit signal
transmit_signal = np.random.uniform(-1, 1, 1000) + 1j * np.random.uniform(-1, 1, 1000)
print(type(transmit_signal))

# transmit from Pluto!
system.transmit_signal(
    transmit_signal
)  # keep transmit signal below 10,000 samples if possible, roughly around +/-1

# receive from Pluto!
receive_signal = system.receive_signal()

# plot transmitted and received signals
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

# take every sps-th sample
receive_symbols = receive_signal[sps // 2 :: sps]
print("Number of receive symbols: ", len(receive_symbols))

# associate received symbols with nearest in the constellation
# %%