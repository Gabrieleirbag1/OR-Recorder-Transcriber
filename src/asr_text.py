import whisper
import os
from utils import OUTPUT_DIR

def transcribe_audio(file_path):
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

if __name__ == "__main__":
    audio_file = os.path.join(OUTPUT_DIR, "output.wav")
    if os.path.exists(audio_file):
        transcription = transcribe_audio(audio_file)
        print("Transcription:", transcription)
    else:
        print(f"Audio file '{audio_file}' not found. Please record audio first.")