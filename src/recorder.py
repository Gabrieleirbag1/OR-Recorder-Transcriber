import sounddevice as sd
import numpy as np
import queue
import threading
from pynput import keyboard

def record_until_key_release(samplerate=16000, trigger_key=keyboard.Key.space):
    """Enregistre tant que la touche est maintenue (simule une pédale)."""
    q = queue.Queue()
    key_pressed = threading.Event()
    key_released_after_press = threading.Event()

    def callback(indata, frames, time, status):
        if key_pressed.is_set():
            q.put(indata.copy())

    def on_press(key):
        if key == trigger_key:
            key_pressed.set()

    def on_release(key):
        if key == trigger_key:
            key_pressed.clear()
            key_released_after_press.set()
            return False  # stoppe le listener

    print(f"Hold '{trigger_key}' to speak...")

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    key_pressed.wait()

    frames = []
    with sd.InputStream(samplerate=samplerate, channels=1, dtype="float32", callback=callback):
        while not key_released_after_press.is_set():
            try:
                frames.append(q.get(timeout=0.1))
            except queue.Empty:
                continue
        while not q.empty():
            frames.append(q.get())

    listener.join()

    if not frames:
        return np.array([], dtype="float32"), samplerate

    audio = np.concatenate(frames, axis=0).flatten()
    return audio, samplerate