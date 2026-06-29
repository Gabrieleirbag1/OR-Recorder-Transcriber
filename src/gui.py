from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
import sys

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
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
            raise ValueError(f"Unknown mode : {mode!r}")

    def setup_recorder_ui(self):
        self.recorder_widget = QWidget()
        layout = QVBoxLayout()
        self.recorder_widget.setLayout(layout)

        record_button = QPushButton("Record")
        record_button.clicked.connect(self.on_record_clicked)
        layout.addWidget(record_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def setup_label_selection_ui(self):
        self.label_selection_widget = QWidget()
        layout = QVBoxLayout()
        self.label_selection_widget.setLayout(layout)

        select_label = QLabel("Select the most appropriate label:")
        layout.addWidget(select_label, alignment=Qt.AlignmentFlag.AlignCenter)

        buttons_layout = QHBoxLayout()
        label_buttons = []
        for i in range(3):
            button = QPushButton(f"Label {i+1}")
            button.clicked.connect(self.nothing)
            label_buttons.append(button)
            buttons_layout.addWidget(button)

        layout.addLayout(buttons_layout)

    def on_record_clicked(self):
        self.show_ui("label_selection")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())