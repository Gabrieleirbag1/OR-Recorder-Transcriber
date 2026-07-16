import json
import os
import re

from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import ASSETS_PATH, THRESHOLD
from nol_event_classifier.supervised.supervised_clustering import SupervisedClustering, RAW_LABELS
from or_recorder_transcriber.event_logger import EventLoggerCSV

with open(os.path.join(ASSETS_PATH, "data", "medical_context.json"), "r", encoding="utf-8") as f:
    MEDICAL_CONTEXT = ' '.join(json.load(f))

class AudioProcessor:
    """Process audio files for automatic speech recognition (ASR) and event classification.
    
    :param asr_model_name str: The name of the ASR model to use.
    :param embedding_model_name str: The name of the embedding model to use for classification.
    :param asr_mode str: The mode of the ASR model (e.g., "faster_whisper", "pywhispercpp", or "whisper").
    :param language str: The language for ASR transcription.
    :param gui bool: Whether the application is running in GUI mode. Defaults to False.
    :param event_logger bool: Whether to log events to a CSV file. Defaults to False.
    """
    def __init__(
            self, 
            asr_model_name: str = "base", 
            embedding_model_name: str = "paraphrase-multilingual-mpnet-base-v2", 
            asr_mode: str = "faster_whisper", 
            language: str = "fr", 
            gui: bool = False, 
            event_logger: bool = False
        ):
        self.asr_model_name = asr_model_name
        self.embedding_model_name = embedding_model_name
        self.asr_mode = asr_mode
        self.language = language
        self.gui = gui
        self.event_logger = EventLoggerCSV() if event_logger else None

        self.asr_model = None
        self.supervised_clustering = None
        self.classification_results: dict = {}
        self.best_event: dict = {}

    def load_models(self):
        """Load the ASR and embedding models based on the specified parameters."""
        self.load_asr_model()
        self.load_embedding_model()

    def load_asr_model(self):
        """Load the ASR model based on the specified mode and model name."""
        if self.asr_mode == "faster_whisper":
            import faster_whisper
            self.asr_model = faster_whisper.WhisperModel(
                self.asr_model_name, 
                device="cpu", 
                cpu_threads=4, 
                compute_type="int8"
            )
        elif self.asr_mode == "pywhispercpp":
            from pywhispercpp.model import Model
            self.asr_model = Model(self.asr_model_name, n_threads=4)
        else:
            import whisper
            self.asr_model = whisper.load_model(self.asr_model_name)
        log(f"ASR model '{self.asr_model_name}' loaded.")

    def load_embedding_model(self):
        """Load the embedding model for event classification."""
        self.supervised_clustering = SupervisedClustering([self.embedding_model_name])
        self.supervised_clustering.load_models(RAW_LABELS)
        log(f"Embedding model '{self.embedding_model_name}' loaded.")

    def transcribe_audio(self, file_path: str) -> str:
        """Transcribe the audio file at the given path using the loaded ASR model.
        
        :param file_path str: The path to the audio file to transcribe.
        
        :return: The transcribed text from the audio file.
        :rtype: str"""
        if self.asr_model is None:
            self.load_asr_model()
            
        if self.asr_mode == "faster_whisper":
            segments, info = self.asr_model.transcribe(
                file_path,
                initial_prompt=MEDICAL_CONTEXT,
                language="fr",
                beam_size=1,
            )
            return " ".join(segment.text for segment in segments).strip()
        elif self.asr_mode == "pywhispercpp":
            result = self.asr_model.transcribe(file_path, initial_prompt=MEDICAL_CONTEXT, language="fr")
            return result[0].text.strip() if result else ""
        else:
            result = self.asr_model.transcribe(file_path, initial_prompt=MEDICAL_CONTEXT, language="fr")
            return result["text"]
    
    def process_audio_to_label(self, file_path: str) -> dict | None:
        """Process the audio file to transcribe it and classify the event, returning the classification results.
        
        :param file_path str: The path to the audio file to process.
        
        :return: The classification results for the processed audio file.
        :rtype: dict | None"""
        text = self.transcribe_audio(file_path)
        log(f"Transcribed : '{text}'")

        if not text:
            return None

        results, _ = self.supervised_clustering.match_events_to_labels([text], RAW_LABELS, self.embedding_model_name, top_k=3)
        log("Classification results: " + str(results[0]), level="DEBUG")
        return results[0]
    
    def log_classification_results(self, result: dict, corrected_label: str | None = None):
        """Log the classification results to the event logger if enabled.

        :param result dict: The classification results to log.
        :param corrected_label str | None: An optional corrected label for the event. Defaults to None."""
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

    def is_label_confident(self, score: float, threshold: float = THRESHOLD) -> bool:
        """Determine if the label is confident based on the score and threshold.

        :param score float: The confidence score of the label.
        :param threshold float: The threshold for determining label confidence. Defaults to THRESHOLD.

        :return: True if the label is confident, False otherwise.
        :rtype: bool"""
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

    def handle_label_selection(self, result: dict) -> dict:
        """Handle the selection of the most appropriate label based on the classification results.

        :param result dict: The classification results containing the top_k labels and their scores.
        
        :return: The selected label from the classification results.
        :rtype: dict"""
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

    def evaluate_audio_event(self, file_path: str) -> dict | None:
        """Evaluate the audio file to transcribe it and classify the event, returning the best event label.

        :param file_path str: The path to the audio file to evaluate.

        :return: The best event label from the classification results, or None if classification failed.
        :rtype: dict | None"""
        self.classification_results = self.process_audio_to_label(file_path)
        if self.classification_results is None:
            log("Unable to classify audio. Please try again.", level="ERROR")
            return None

        self.best_event = self.handle_label_selection(self.classification_results)
        return self.best_event