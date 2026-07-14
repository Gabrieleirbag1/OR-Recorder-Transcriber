import whisper
import faster_whisper
from pywhispercpp.model import Model
import time
import os
from lite_logging.lite_logging import log

file_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "audio", "output_copy.wav")
print(os.path.abspath(file_path))


def load_whisper_model(model_name="base"):
    model = whisper.load_model(model_name)
    log(f"Whisper model '{model_name}' loaded.")
    return model

def load_faster_whisper_model(model_name="base"):
    model = faster_whisper.WhisperModel(model_name)
    log(f"Faster Whisper model '{model_name}' loaded.")
    return model

def load_pywhispercpp_model(model_name="base"):
    model = Model('base', n_threads=6)
    log(f"PyWhisperCpp model '{model_name}' loaded.")
    return model

def transcribe_audio(file_path, model):
    chronomètre = time.time()
    result = model.transcribe(file_path)
    log(f"Audio processed in {time.time() - chronomètre:.2f} seconds.")
    return result

whisper_model = load_whisper_model("base")
faster_whisper_model = load_faster_whisper_model("base")
pywhispercpp_model = load_pywhispercpp_model("base")
transcribed_whisper = transcribe_audio(file_path, whisper_model)
transcribed_faster_whisper = transcribe_audio(file_path, faster_whisper_model)
transcribed_pywhispercpp = transcribe_audio(file_path, pywhispercpp_model)