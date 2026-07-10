import soundfile as sf
import os
import argparse
from lite_logging.lite_logging import log
from or_recorder_transcriber.recorder import record_until_key_release
from or_recorder_transcriber.asr_text import AudioProcessor
from or_recorder_transcriber.utils import AUDIO_DIR

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

def gui():
    import sys
    from PySide6.QtWidgets import QApplication
    from or_recorder_transcriber.gui import Window  

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

def main():
    parser = argparse.ArgumentParser(description="Fine-tune a SetFit model on a training dataset")
    parser.add_argument('--cli', "-c", action='store_true', help='Run in command-line interface mode')
    args = parser.parse_args()
    if args.cli:
        cli()
    else:
        gui()
    
if __name__ == "__main__":
    main()
