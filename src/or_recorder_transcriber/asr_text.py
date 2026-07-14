import json
import os
import re
import faster_whisper
import whisper
from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import ASSETS_PATH, AUDIO_DIR, THRESHOLD
from nol_event_classifier.supervised.supervised_clustering import SupervisedClustering, RAW_LABELS
from or_recorder_transcriber.event_logger import EventLoggerCSV

with open(os.path.join(ASSETS_PATH, "data", "medical_context.json"), "r", encoding="utf-8") as f:
    MEDICAL_CONTEXT = ' '.join(json.load(f))

ASR_MODE = "faster_whisper"  # or "whisper"

class AudioProcessor:
    def __init__(self, asr_model_name="base", embedding_model_name="paraphrase-multilingual-mpnet-base-v2", gui=False, event_logger=False):
        self.asr_model_name = asr_model_name
        self.embedding_model_name = embedding_model_name
        self.gui = gui
        self.asr_model = None
        self.event_logger = EventLoggerCSV() if event_logger else None
        self.supervised_clustering = None
        self.classification_results: dict = {}
        self.best_event: dict = {}

    def load_models(self):
        self.load_asr_model()
        self.load_embedding_model()

    def load_asr_model(self):
        if ASR_MODE == "faster_whisper":
            self.asr_model = faster_whisper.WhisperModel(self.asr_model_name)
        else:
            self.asr_model = whisper.load_model(self.asr_model_name)
        self.asr_model = whisper.load_model(self.asr_model_name)
        log(f"ASR model '{self.asr_model_name}' loaded.")

    def load_embedding_model(self):
        self.supervised_clustering = SupervisedClustering([self.embedding_model_name])
        self.supervised_clustering.load_models(RAW_LABELS)
        log(f"Embedding model '{self.embedding_model_name}' loaded.")

    def transcribe_audio(self, file_path) -> str:
        if self.asr_model is None:
            self.load_asr_model()
        if ASR_MODE == "faster_whisper":
            result = self.asr_model.transcribe(file_path, initial_prompt=MEDICAL_CONTEXT)
            return result["text"]
    
    def process_audio_to_label(self, file_path) -> dict | None:
        text = self.transcribe_audio(file_path)
        log(f"Transcribed : '{text}'")

        if not text:
            return None

        results, _ = self.supervised_clustering.match_events_to_labels([text], RAW_LABELS, self.embedding_model_name, top_k=3)
        log("Classification results: " + str(results[0]), level="DEBUG")
        return results[0]
    
    def log_classification_results(self, result, corrected_label=None):
        if self.event_logger:
            text = result["event_raw"] #propofol 0.05 mg 
            dose = re.search(r'(\d+(\.\d+)?)\s*(mg|g|ml|l|units)?', text)
            dose = dose.group(0) if dose else "N/A"

            self.event_logger.append_to_csv_file(
                event=result["event_raw"],
                dose=dose,
                event_type="N/A",
                selected_label=result["top_k"][0]["label"],
                score=result["top_k"][0]["score"],
                corrected_label=corrected_label
            )

    def is_label_confident(self, score, threshold=THRESHOLD) -> bool:
        if score <= threshold:
            log(f"Score {score:.2f} is below the threshold {threshold}. Label is not confident.", level="DEBUG")
            return False
        events = self.classification_results["top_k"]
        for i in range(1, len(self.classification_results["top_k"])):
            diff = self.classification_results["best_score"] - events[i]["score"]
            if diff < 0.3:
                log(f"Score difference {diff:.2f} between best score and '{events[i]['label']}' is less than 0.3. Label is not confident.", level="DEBUG")
                return False
        return True

    def handle_label_selection(self, result):
        best_score = float(result["best_score"])
        if not self.gui and not self.is_label_confident(best_score):
            print("Please select the most appropriate label from the following options:")
            for (i, event) in enumerate(result["top_k"]):
                print(f"[{i+1}] Label: {event['label']}, Score: {event['score']}")
            else:
                input_str = input("Enter the number of the selected label (or press Enter to skip): ")
                if input_str.strip().isdigit():
                    selected_index = int(input_str.strip()) - 1
                    if 0 <= selected_index < len(result["top_k"]):
                        selected_label = result["top_k"][selected_index]
                        log(f"User selected label: {selected_label}", level="DEBUG")
                        self.log_classification_results(result, corrected_label=selected_label["label"])
                        return selected_label
                    else:
                        log("Invalid selection. No label selected.", level="WARNING")
                else:
                    log("No label selected by user.", level="WARNING")
        if not self.gui:
            self.log_classification_results(result)
        return result["top_k"][0]

    def evaluate_audio_event(self, file_path):
        self.classification_results = self.process_audio_to_label(file_path)
        if self.classification_results is None:
            log("Unable to classify audio. Please try again.", level="ERROR")
            return None

        self.best_event = self.handle_label_selection(self.classification_results)
        return self.best_event

if __name__ == "__main__":
    audio_file = os.path.join(AUDIO_DIR, "output.wav")
    if os.path.exists(audio_file):
        audio_processor = AudioProcessor(event_logger=True)
        audio_processor.load_models()
        best_event, result = audio_processor.evaluate_audio_event(audio_file)
        log(f"Best event: {best_event['label']} (score: {best_event['score']:.2f})")
    else:
        log(f"Audio file '{audio_file}' not found. Please record audio first.", level="ERROR")