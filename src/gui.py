from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
import sys

from recorder import RecordThread

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.record_thread = None
        self.setup_ui()

    def nothing(self):
        pass

    def setup_size(self):
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        width = int(screen_size.width() * 0.5)
        height = int(screen_size.height() * 0.5)
        self.setGeometry(100, 100, width, height)

    def setup_ui(self):
        self.setup_size()
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
        layout = QVBoxLayout()
        self.recorder_widget.setLayout(layout)

        self.record_button = QPushButton("Hold to Record")
        self.record_button.pressed.connect(self.on_record_pressed)
        self.record_button.released.connect(self.on_record_released)
        layout.addWidget(self.record_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def setup_label_selection_ui(self):
        self.label_selection_widget = QWidget()
        layout = QVBoxLayout()
        self.label_selection_widget.setLayout(layout)

        select_label = QLabel("Select the most appropriate label:")
        layout.addWidget(select_label, alignment=Qt.AlignmentFlag.AlignCenter)

        buttons_layout = QHBoxLayout()
        self.label_buttons = []
        for i in range(3):
            button = QPushButton(f"Label {i+1}")
            button.clicked.connect(self.nothing)
            self.label_buttons.append(button)
            buttons_layout.addWidget(button)

        layout.addLayout(buttons_layout)

    def on_record_pressed(self):
        self.status_label.setText("Recording...")
        self.record_thread = RecordThread(samplerate=16000, filename="output.wav")
        self.record_thread.finished_recording.connect(self.on_recording_finished)
        self.record_thread.recording_failed.connect(self.on_recording_failed)
        self.record_thread.start()

    def on_record_released(self):
        self.status_label.setText("Processing...")
        if self.record_thread is not None:
            self.record_thread.stop()

    def on_recording_finished(self, file_path):
        self.status_label.setText(f"Saved : {file_path}")

        # result = process_audio_to_label(file_path)
        # for button, candidate in zip(self.label_buttons, result["top_k"]):
        #     button.setText(candidate["label"])

        self.show_ui("label_selection")

    def on_recording_failed(self, error_message):
        self.status_label.setText(f"Recording failed : {error_message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())