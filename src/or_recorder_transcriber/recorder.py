import sounddevice as sd
import numpy as np
import queue
import threading
from pynput import keyboard
from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import AUDIO_DIR

import os
import queue
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from PySide6.QtCore import QThread, Signal

class RecordThread(QThread):
    """Thread for recording audio using sounddevice.
    
    :param samplerate int: The sample rate for recording.
    :param filename string: The name of the output file.
    :param parent object: The parent widget.
    """
    finished_recording = Signal(str)
    recording_failed = Signal(str)

    def __init__(self, samplerate: int = 16000, filename: str = "output.wav", parent: object = None):
        """Initialize the RecordThread with the given parameters.
        
        :param samplerate int: The sample rate for recording.
        :param filename string: The name of the output file.
        :param parent object: The parent widget.
        """
        super().__init__(parent)
        self.samplerate = samplerate
        self.filename = filename
        self._stop_event = threading.Event()

    def run(self) -> None:
        """Start recording audio until the stop event is set."""
        self._stop_event.clear()

        q = queue.Queue()

        def callback(indata: np.ndarray, frames: int, time: float, status: str):
            """Handle the audio input stream callback. Put the audio data into the queue.
            
            :param indata: The recorded audio data.
            :param frames: The number of frames recorded.
            :param time: The time information for the callback.
            :param status: The status of the audio input stream.
            """
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
        """Stop the recording."""
        if self._stop_event is not None:
            self._stop_event.set()

def record_until_key_release(samplerate: int = 16000, trigger_key: keyboard.Key = keyboard.Key.space) -> tuple[np.ndarray, int]:
    """Record audio until the specified trigger key is released.
    
    :param samplerate int: The sample rate for recording.
    :param trigger_key keyboard.Key: The key that triggers the recording.

    :return: A tuple containing the recorded audio data and the sample rate.
    :rtype: tuple[np.ndarray, int]
    """
    q = queue.Queue()
    key_pressed = threading.Event()
    key_released_after_press = threading.Event()

    def callback(indata: np.ndarray, frames: int, time: float, status: str):
        """Handle the audio input stream callback. If the trigger key is pressed, put the audio data into the queue.
        
        :param indata np.ndarray: The recorded audio data.
        :param frames int: The number of frames recorded.
        :param time float: The time information for the callback.
        :param status str: The status of the audio input stream."""
        if key_pressed.is_set():
            q.put(indata.copy())

    def on_press(key: keyboard.Key):
        """Handle the key press event. If the trigger key is pressed, set the key_pressed event.
        
        :param key keyboard.Key: The key that was pressed."""
        if key == trigger_key:
            key_pressed.set()

    def on_release(key: keyboard.Key) -> bool:
        """Handle the key release event. If the trigger key is released, stop the listener.
        
        :param key keyboard.Key: The key that was released.
        
        :return: False to stop the listener if the trigger key is released, True otherwise.
        :rtype: bool
        """
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