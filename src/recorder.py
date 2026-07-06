import sounddevice as sd
import numpy as np
import queue
import threading
from pynput import keyboard
from lite_logging.lite_logging import log
from utils import AUDIO_DIR

import os
import queue
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt6.QtCore import QThread, pyqtSignal

class RecordThread(QThread):
    finished_recording = pyqtSignal(str)
    recording_failed = pyqtSignal(str)

    def __init__(self, samplerate=16000, filename="output.wav", parent=None):
        super().__init__(parent)
        self.samplerate = samplerate
        self.filename = filename
        self._stop_event = threading.Event()

    def run(self):
        self._stop_event.clear()

        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                log(f"Sounddevice status: {status}")
            q.put(indata.copy())

        log("Recording started...")

        frames = []
        try:
            with sd.InputStream(samplerate=self.samplerate, channels=1, dtype="float32", callback=callback):
                while not self._stop_event.is_set():
                    try:
                        frames.append(q.get(timeout=0.1))
                    except queue.Empty:
                        continue
                while not q.empty():
                    frames.append(q.get())
        except Exception as e:
            log(f"Recording error: {e}", level="ERROR")
            self.recording_failed.emit(str(e))
            return

        if not frames:
            log("No audio captured.", level="ERROR")
            self.recording_failed.emit("No audio captured.")
            return

        audio = np.concatenate(frames, axis=0).flatten()
        duration = len(audio) / self.samplerate
        log(f"Recording ended. Duration: {duration:.2f} seconds.")

        output_path = os.path.join(AUDIO_DIR, self.filename)
        sf.write(output_path, audio, self.samplerate)
        log(f"File '{output_path}' saved.", level="DEBUG")

        self.finished_recording.emit(output_path)

    def stop(self):
        if self._stop_event is not None:
            self._stop_event.set()

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

    log(f"=========== Hold '{trigger_key}' to speak... ===========")

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

if __name__ == "__main__":
    audio, sr = record_until_key_release()
    log(f"Recording ended. Duration: {len(audio) / sr:.2f} seconds.")
    # save the file 
    sf.write(os.path.join(AUDIO_DIR, "output.wav"), audio, sr)
    log("File 'output.wav' saved.", level="DEBUG")