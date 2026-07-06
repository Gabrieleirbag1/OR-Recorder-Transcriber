import soundfile as sf
import os
from lite_logging.lite_logging import log
from recorder import record_until_key_release
from asr_text import AudioProcessor
from utils import AUDIO_DIR

def cli():
    audio_processor = AudioProcessor(event_logger=True)
    audio_processor.load_models()

    while True:
        audio, sr = record_until_key_release()
        log(f"Recording ended. Duration: {len(audio) / sr:.2f} seconds.")

        output_file_path = os.path.join(AUDIO_DIR, "output.wav")
        sf.write(output_file_path, audio, sr)
        log("File 'output.wav' saved.", level="DEBUG")

        result = audio_processor.evaluate_audio_event(output_file_path)

        log(f"Classification results: {result}")

def main():
    cli()
    
if __name__ == "__main__":
    main()
