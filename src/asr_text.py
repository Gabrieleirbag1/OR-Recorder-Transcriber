import json
import os
import whisper
from lite_logging.lite_logging import log
from utils import OUTPUT_DIR, THRESHOLD
from nol_event_classifier.supervised.supervised_clustering import match_events_to_labels, RAW_LABELS

with open(os.path.join(os.path.dirname(__file__), "medical_context.json"), "r", encoding="utf-8") as f:
    MEDICAL_CONTEXT = ' '.join(json.load(f))

class AudioProcessor:
    def __init__(self, model_name_asr="base", model_name_embedding="paraphrase-multilingual-mpnet-base-v2", gui=False):
        self.model_name_asr = model_name_asr
        self.model_name_embedding = model_name_embedding
        self.gui = gui
        self.asr_model = None
        self.best_event: dict = {}
        self.events: list[dict] = [{}]

    def load_model(self):
        self.asr_model = whisper.load_model(self.model_name_asr)
        log(f"ASR model '{self.model_name_asr}' loaded.")

    def transcribe_audio(self, file_path) -> str:
        if self.asr_model is None:
            self.load_model()
        result = self.asr_model.transcribe(file_path, initial_prompt=MEDICAL_CONTEXT)
        return result["text"]
    
    def process_audio_to_label(self, file_path) -> dict | None:
        text = self.transcribe_audio(file_path)
        log(f"Transcribed : '{text}'")

        if not text:
            return None

        results, _ = match_events_to_labels([text], RAW_LABELS, self.model_name_embedding, top_k=3)
        self.events = results[0]["top_k"]
        log("Classification results: " + str(results[0]))
        return results[0]

    def handle_label_selection(self, result):
        best_score = float(result["best_score"])
        if best_score >= THRESHOLD and not self.gui:
            print("Please select the most appropriate label from the following options:")
            for (i, event) in enumerate(result["top_k"]):
                print(f"[{i+1}] Label: {event['label']}, Score: {event['score']}")
            else:
                input_str = input("Enter the number of the selected label (or press Enter to skip): ")
                if input_str.strip().isdigit():
                    selected_index = int(input_str.strip()) - 1
                    if 0 <= selected_index < len(result["top_k"]):
                        selected_label = result["top_k"][selected_index]
                        log(f"User selected label: {selected_label}")
                        return selected_label
                    else:
                        log("Invalid selection. No label selected.")
                else:
                    log("No label selected by user.")
        return result["top_k"][0]

    def evaluate_audio_event(self, file_path):
        result = self.process_audio_to_label(file_path)
        if result is None:
            log("Unable to classify audio. Please try again.")
            return None

        self.best_event = self.handle_label_selection(result)
        return self.best_event

if __name__ == "__main__":
    audio_file = os.path.join(OUTPUT_DIR, "output.wav")
    if os.path.exists(audio_file):
        audio_processor = AudioProcessor()
        result = audio_processor.evaluate_audio_event(audio_file)
        log(f"Best event: {result['label']} (score: {result['score']:.2f})")
    else:
        log(f"Audio file '{audio_file}' not found. Please record audio first.", level="ERROR")