import json
import os
import re
from PySide6.QtCore import QObject
from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import ASSETS_PATH
from nol_event_classifier.supervised.supervised_clustering import SupervisedClustering, RAW_LABELS
from or_recorder_transcriber.event_logger import EventLoggerCSV

with open(os.path.join(ASSETS_PATH, "data", "medical_context.json"), "r", encoding="utf-8") as f:
    MEDICAL_CONTEXT = ' '.join(json.load(f))

class AudioProcessor(QObject):
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
        event_types: dict | None = None,
        gui: bool = False, 
        event_logger: bool = False
    ):
        """Initialize the AudioProcessor with the given configuration.
        
        :param asr_model_name str: The name of the ASR model to use.
        :param embedding_model_name str: The name of the embedding model to use for classification.
        :param asr_mode str: The mode of the ASR model (e.g., "faster_whisper", "pywhispercpp", or "whisper").
        :param language str: The language for ASR transcription.
        :param event_types dict | None: Mapping of label name to Event Type ("Medication" / "Other"),
            loaded once by the caller (e.g. MainWindow) from labels.json. Used to resolve the Event
            Type logged for each classified event. Defaults to None.
        :param gui bool: Whether the application is running in GUI mode. Defaults to False.
        :param event_logger bool: Whether to log events to a CSV file. Defaults to False.
        """
        super().__init__()
        self.asr_model_name = asr_model_name
        self.embedding_model_name = embedding_model_name
        self.asr_mode = asr_mode
        self.language = language
        self.event_types = event_types or {}
        self.gui = gui
        self.event_logger = EventLoggerCSV() if event_logger else None

        self.asr_model = None
        self.supervised_clustering = None
        self.classification_results: dict = {}
        self.best_event: dict = {}
        self.text_queue: list[str] = []

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
        return "procedure propofol 0.05 mg et incision et fentanyl 1mg"  # Placeholder for actual transcription logic
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
    
    def transcribe_and_classify_audio(self, file_path: str) -> tuple[dict, str] | None:
        """Process the audio file to transcribe it and classify the event, returning the classification results.
        
        :param file_path str: The path to the audio file to process.
        
        :return: The classification results for the processed audio file or None if classification failed.
        :rtype: tuple[dict, str] | None"""
        self.text_queue = []
        text = self.transcribe_audio(file_path)
        log(f"Transcribed : '{text}'")

        if not text:
            return None, text

        if (" et " in text):
            self.text_queue = text.split(" et ")
            text = self.text_queue[0]
            self.text_queue.pop(0)

        return self.process_text_to_label(text), text

    def process_text_to_label(self, text: str) -> dict | None:
        """Process the given text to classify the event, returning the classification results.

        :param text str: The text to classify.

        :return: The classification results for the given text.
        :rtype: dict | None"""
        if not text:
            return None

        results, _ = self.supervised_clustering.match_events_to_labels([text], RAW_LABELS, self.embedding_model_name, top_k=3)
        log("Classification results: " + str(results[0]), level="DEBUG")
        return results[0]
    
    def log_classification_results(self, result: dict, corrected_label: str | None = None):
        """Log the classification results to the event logger if enabled. The Event Type is resolved
        from the effective label (corrected label if provided, otherwise the top-scoring label) via
        the event_types mapping loaded from labels.json.

        :param result dict: The classification results to log.
        :param corrected_label str | None: An optional Corrected Label for the event. Defaults to None."""
        if self.event_logger:
            text = result["event_raw"] #propofol 0.05 mg 
            dose = re.search(r'(\d+(\.\d+)?)\s*(mg|g|ml|l|units)?', text)
            dose = dose.group(0) if dose else "N/A"

            effective_label = corrected_label if corrected_label is not None else result["top_k"][0]["label"]
            event_type = self.event_types.get(effective_label, "Other")

            self.event_logger.append_to_csv_file(
                event=result["event_raw"],
                dose=dose,
                event_type=event_type,
                selected_label=result["top_k"][0]["label"],
                score=result["top_k"][0]["score"],
                corrected_label=corrected_label
            )

    def is_label_confident(self, score: float, threshold: float = 0.75) -> bool:
        """Determine if the label is confident based on the score and threshold.

        :param score float: The confidence score of the label.
        :param threshold float: The threshold for determining label confidence. Defaults to 0.75.

        :return: True if the label is confident, False otherwise.
        :rtype: bool"""
        log(f"Checking label confidence: score={score:.2f}, threshold={threshold}", level="DEBUG")
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

    def evaluate_audio_event(self, file_path: str = None, text: str = None) -> tuple[dict, str] | None:
        """Evaluate the audio file to transcribe it and classify the event, returning the best event label.

        :param file_path str: The path to the audio file to evaluate.
        :param text str: The text to classify.

        :return: The best event label from the classification results, along with the transcribed text, or None if classification failed.
        :rtype: tuple[dict, str] | None"""
        if file_path is None and text is None:
            raise ValueError("Either file_path or text must be provided.")
        if text is None:
            self.classification_results, text = self.transcribe_and_classify_audio(file_path)
        else:
            self.classification_results = self.process_text_to_label(text)
        if self.classification_results is None:
            log("Unable to classify audio. Please try again.", level="ERROR")
            return None, text

        self.best_event = self.handle_label_selection(self.classification_results)
        return self.best_event, text

    def generate_graphs(self):
        """Generate graphs for each unique Event Type in the CSV file if the event logger is enabled."""
        if self.event_logger:
            self.event_logger.generate_graphs()