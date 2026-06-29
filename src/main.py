import soundfile as sf
import os
from lite_logging.lite_logging import log
from recorder import record_until_key_release
from asr_text import process_audio_to_label, handle_label_selection
from utils import OUTPUT_DIR

def cli():
    audio, sr = record_until_key_release()
    log(f"Recording ended. Duration: {len(audio) / sr:.2f} seconds.")

    output_file_path = os.path.join(OUTPUT_DIR, "output.wav")
    sf.write(output_file_path, audio, sr)
    log("File 'output.wav' saved.")

    result = process_audio_to_label(output_file_path)
    log(f"Classification results: {result}")

    best_label = handle_label_selection(result)
    log(f"Final selected label: {best_label}")

def main():
    cli()
    
if __name__ == "__main__":
    main()
