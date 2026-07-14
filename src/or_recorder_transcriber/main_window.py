from PySide6.QtWidgets import QApplication, QComboBox, QFileDialog, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QFont
from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import ASSETS_PATH, AUDIO_DIR, CONFIG_PATH
from or_recorder_transcriber.recorder import RecordThread
from or_recorder_transcriber.asr_text import AudioProcessor
import os
import json

with open(os.path.join(ASSETS_PATH, "data", "labels.json"), "r", encoding="utf-8") as f:
    RAW_LABELS = json.load(f)

class MainWindow(QMainWindow):
    def __init__(self, config, theme="light"):
        super().__init__()
        self.theme = theme
        self.config = config

        self.record_thread = None
        self.audio_processor = None
        self.is_recording = False

        self.setWindowTitle("OR Recorder Transcriber")
        self.setup()

    def setup(self):
        self.load_audio_processor()
        self.setup_size()
        self.setup_ui()

    def load_audio_processor(self):
        if self.audio_processor is None:
            self.audio_processor = AudioProcessor(
                asr_model_name=self.config["asr_model_name"],
                embedding_model_name=self.config["embedding_model_name"],
                asr_mode=self.config["asr_mode"],
                language=self.config["language"],
                gui=True, 
                event_logger=True
            )
        self.audio_processor.load_asr_model()
        self.audio_processor.load_embedding_model()

    def setup_size(self):
        self.setMaximumSize(960, 640)
        ## check screen size and set window size accordingly
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        if screen_size.width() < 960 or screen_size.height() < 640:
            self.setMaximumSize(screen_size.width(), screen_size.height())
            self.setFixedSize(screen_size.width(), screen_size.height() - 100)
            self.setFont(QFont("Arial", 12))
        else:
            self.resize(960, 640)
            self.setFont(QFont("Arial", 16))

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)

        self.setup_recorder_ui()
        self.setup_label_selection_ui()

        self.main_layout.addWidget(self.recorder_widget)
        self.main_layout.addWidget(self.label_selection_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(main_widget)
        self.show_ui("recorder")

    def show_ui(self, mode):
        if mode == "recorder":
            self.recorder_widget.show()
            self.label_selection_widget.hide()
        elif mode == "label_selection":
            self.recorder_widget.hide()
            self.label_selection_widget.show()
        else:
            raise ValueError(f"Mode inconnu : {mode!r} (attendu : 'recorder' ou 'label_selection')")

    def setup_recorder_ui(self):
        self.recorder_widget = QWidget()
        self.recorder_layout = QVBoxLayout()
        self.recorder_widget.setLayout(self.recorder_layout)

        mic_pixmap = QPixmap(os.path.join(ASSETS_PATH, "images", f"mic_{self.theme}.svg"))
        self.mic_icon = QIcon(mic_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        stop_pixmap = QPixmap(os.path.join(ASSETS_PATH, "images", f"stop_{self.theme}.svg"))
        self.stop_icon = QIcon(stop_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.record_button = QPushButton()
        self.record_button.setFixedSize(120, 120)
        self.record_button.setIcon(self.mic_icon)
        self.record_button.setIconSize(mic_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation).size())
        self.record_button.clicked.connect(self.on_record_clicked)
        self.recorder_layout.addWidget(self.record_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("")
        self.recorder_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def setup_label_selection_ui(self):
        self.label_selection_widget = QWidget()
        self.label_selection_layout = QVBoxLayout()
        self.label_selection_layout.setSpacing(10)
        self.label_selection_widget.setLayout(self.label_selection_layout)
        self.label_selection_widget.setFixedWidth(self.width() * 2 // 3)

        self.select_label = QLabel("Select the most appropriate label:")
        self.label_selection_layout.addWidget(self.select_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.buttons_layout = QVBoxLayout()
        self.label_buttons = []
        for i in range(3):
            button = QPushButton(f"Label {i+1}")
            button.clicked.connect(lambda _, btn=button: self.on_label_selected(btn))
            self.label_buttons.append(button)
            self.buttons_layout.addWidget(button)

        self.label_combobox_selection_widget = QWidget()
        self.label_combobox_selection_layout = QHBoxLayout()
        self.label_combobox_selection_layout.setSpacing(10)
        self.label_combobox_selection_widget.setLayout(self.label_combobox_selection_layout)

        self.labels_combobox = QComboBox()
        self.labels_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.labels_combobox.addItems(RAW_LABELS)

        self.confirm_button = QPushButton("Ok")
        self.confirm_button.clicked.connect(lambda: self.on_label_selected(self.labels_combobox))

        self.label_combobox_selection_layout.addWidget(self.labels_combobox)
        self.label_combobox_selection_layout.addWidget(self.confirm_button)

        self.label_selection_layout.addLayout(self.buttons_layout)
        self.label_selection_layout.addWidget(self.label_combobox_selection_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_label_selected(self, element: QPushButton | QComboBox):
        if isinstance(element, QPushButton):
            best_label = element.text()
        else:
            best_label = element.currentText()
        self.status_label.setText(f"Selected label: {best_label}")
        log(f"User selected label: {best_label}", level="DEBUG")
        if self.audio_processor.event_logger:
            best_label = best_label if self.audio_processor.classification_results["best_label"] != best_label else None
            self.audio_processor.log_classification_results(self.audio_processor.classification_results, corrected_label=best_label)
        self.show_ui("recorder")

    def on_record_clicked(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.setIcon(self.stop_icon)
        self.status_label.setText("Recording...")
        self.record_button.setStyleSheet("background-color: red")

        self.record_thread = RecordThread(samplerate=16000, filename="output.wav")
        self.record_thread.finished_recording.connect(self.on_recording_finished)
        self.record_thread.recording_failed.connect(self.on_recording_failed)
        self.record_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.record_button.setIcon(self.mic_icon)
        self.record_button.setStyleSheet("")
        self.status_label.setText("Processing...")
        if self.record_thread is not None:
            self.record_thread.stop()

    def on_recording_finished(self, file_path):
        self.status_label.setText(f"Saved : {file_path}")

        file_path = os.path.join(os.path.dirname(__file__), AUDIO_DIR, "output_copy.wav")

        best_event = self.audio_processor.evaluate_audio_event(file_path)
        if best_event is None:
            self.status_label.setText(f"Unable to classify audio. Please try again.")
            return

        if self.audio_processor.is_label_confident(float(best_event["score"])):
            self.status_label.setText(f"Best label: {best_event['label']} (score: {best_event['score']:.2f})")
            if self.audio_processor.event_logger:
                self.audio_processor.log_classification_results(self.audio_processor.classification_results)
            return

        for button, event in zip(self.label_buttons, self.audio_processor.classification_results["top_k"]):
            button.setText(event["label"])

        self.show_ui("label_selection")

    def on_recording_failed(self, error_message):
        self.status_label.setText(f"Recording failed : {error_message}")