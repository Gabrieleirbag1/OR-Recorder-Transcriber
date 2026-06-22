from recorder import record_until_key_release
from asr_text import process_audio_to_label
import soundfile as sf
import os

from utils import OUTPUT_DIR

def main():
    audio, sr = record_until_key_release()
    print(f"Recording ended. Duration: {len(audio) / sr:.2f} seconds.")

    output_file_path = os.path.join(OUTPUT_DIR, "output.wav")
    sf.write(output_file_path, audio, sr)
    print("File 'output.wav' saved.")

    result = process_audio_to_label(output_file_path)
    print("Classification results:", result)

if __name__ == "__main__":
    main()
