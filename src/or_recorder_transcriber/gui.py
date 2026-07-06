from PyQt6.QtWidgets import QApplication, QComboBox, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import THRESHOLD
from or_recorder_transcriber.recorder import RecordThread
from or_recorder_transcriber.asr_text import AudioProcessor
import os
import sys
import json

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
with open(os.path.join(os.path.dirname(__file__), "labels.json"), "r", encoding="utf-8") as f:
    RAW_LABELS = json.load(f)
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.record_thread = None
        self.best_label = None
        self.audio_processor = None

        self.setWindowTitle("OR Recorder Transcriber")
        self.setup()

    def setup(self):
        self.load_audio_processor()
        self.setup_size()
        self.setup_ui()

    def load_audio_processor(self):
        self.audio_processor = AudioProcessor(gui=True)
        self.audio_processor.load_asr_model()
        self.audio_processor.load_embedding_model()

    def setup_size(self):
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        width = int(screen_size.width() * 0.5)
        height = int(screen_size.height() * 0.5)
        self.setGeometry(100, 100, width, height)

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)

        self.setup_recorder_ui()
        self.setup_label_selection_ui()

        self.main_layout.addWidget(self.recorder_widget)
        self.main_layout.addWidget(self.label_selection_widget)

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

        self.micro_image_pixmap = QPixmap(os.path.join(ASSETS_PATH, "mic_dark.svg"))
        self.record_button = QPushButton()
        self.record_button.setFixedSize(120, 120)
        self.micro_image_pixmap = self.micro_image_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.record_button.setIcon(QIcon(self.micro_image_pixmap))
        self.record_button.setIconSize(self.micro_image_pixmap.size())
        self.record_button.pressed.connect(self.on_record_pressed)
        self.record_button.released.connect(self.on_record_released)
        self.recorder_layout.addWidget(self.record_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("")
        self.recorder_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def setup_label_selection_ui(self):
        self.label_selection_widget = QWidget()
        self.label_selection_layout = QVBoxLayout()
        self.label_selection_widget.setLayout(self.label_selection_layout)

        self.select_label = QLabel("Select the most appropriate label:")
        self.label_selection_layout.addWidget(self.select_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.buttons_layout = QHBoxLayout()
        self.label_buttons = []
        for i in range(3):
            button = QPushButton(f"Label {i+1}")
            button.clicked.connect(lambda _, btn=button: self.on_label_selected(btn))
            self.label_buttons.append(button)
            self.buttons_layout.addWidget(button)

        self.label_combobox_selection_widget = QWidget()
        self.label_combobox_selection_layout = QHBoxLayout()
        self.label_combobox_selection_widget.setLayout(self.label_combobox_selection_layout)

        self.labels_combobox = QComboBox()
        self.labels_combobox.addItems(RAW_LABELS)

        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(lambda: self.on_label_selected(self.labels_combobox))

        self.label_combobox_selection_layout.addWidget(self.labels_combobox)
        self.label_combobox_selection_layout.addWidget(self.confirm_button)

        self.label_selection_layout.addLayout(self.buttons_layout)
        self.label_selection_layout.addWidget(self.label_combobox_selection_widget, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_label_selected(self, element: QPushButton | QComboBox):
        if isinstance(element, QPushButton):
            self.best_label = element.text()
        else:
            self.best_label = element.currentText()
        self.status_label.setText(f"Selected label: {self.best_label}")
        self.show_ui("recorder")
        log(f"User selected label: {self.best_label}", level="DEBUG")

    def on_record_pressed(self):
        self.status_label.setText("Recording...")
        self.record_button.setStyleSheet("background-color: red")
        self.record_thread = RecordThread(samplerate=16000, filename="output.wav")
        self.record_thread.finished_recording.connect(self.on_recording_finished)
        self.record_thread.recording_failed.connect(self.on_recording_failed)
        self.record_thread.start()

    def on_record_released(self):
        self.status_label.setText("Processing...")
        self.record_button.setStyleSheet("")
        if self.record_thread is not None:
            self.record_thread.stop()

    def on_recording_finished(self, file_path):
        self.status_label.setText(f"Saved : {file_path}")
        
        file_path = "/home/frigiel/Documents/VSCODE/Stage LIAM 2026/OR-Recorder-Transcriber/output/audio/output copy.wav"

        result = self.audio_processor.evaluate_audio_event(file_path)
        if result is None:
            self.status_label.setText(f"Unable to classify audio. Please try again.")
            return
        
        if float(result["score"]) >= THRESHOLD:
            self.status_label.setText(f"Best label: {result['label']} (score: {result['score']:.2f})")
            return
        
        for button, event in zip(self.label_buttons, self.audio_processor.events):
            button.setText(event["label"])

        self.show_ui("label_selection")

    def on_recording_failed(self, error_message):
        self.status_label.setText(f"Recording failed : {error_message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())