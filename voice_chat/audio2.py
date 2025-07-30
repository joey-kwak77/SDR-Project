from pynput import keyboard as kb
import threading, queue, numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ---------------------------------------------
fs, chunk = 44100, 1024
q     = queue.Queue(maxsize=8)       # audio frames
talk  = threading.Event()            # True while space is held
levels = 256                         # 8‑bit ADC

# keyboard handlers (UI thread)
def on_press(key):
    if key == kb.Key.space:
        talk.set()
def on_release(key):
    if key == kb.Key.space:
        talk.clear()
kb.Listener(on_press=on_press, on_release=on_release, daemon=True).start()

# audio callback (real‑time thread)
def audio_cb(indata, frames, time, status):
    try:
        q.put_nowait(indata.copy())
    except queue.Full:
        pass                         # drop frame if UI is slow

# quantiser
def quantise(sig):
    return np.round(sig*(levels/2-1))/(levels/2-1)

# plotting
fig, ax = plt.subplots()
x = np.arange(chunk)
raw,   = ax.plot(x, np.zeros(chunk))
quant, = ax.plot(x, np.zeros(chunk), '--')
ax.set(xlim=(0, chunk), ylim=(-1, 1))

def update(_):
    if q.empty():
        return raw, quant
    buf = q.get()[:, 0]
    if not talk.is_set():            # mute unless space pressed
        buf[:] = 0
    raw.set_ydata(buf)
    qsig = quantise(buf)
    quant.set_ydata(qsig)
    return raw, quant

ani = animation.FuncAnimation(fig, update, interval=10)
with sd.InputStream(callback=audio_cb, channels=1,
                    samplerate=fs, blocksize=chunk):
    plt.show()
