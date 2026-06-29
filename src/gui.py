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
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        select_label = QLabel("Select the most appropriate label:")
        main_layout.addWidget(select_label, alignment=Qt.AlignmentFlag.AlignCenter)

        buttons_layout = QHBoxLayout()
        label_buttons = []
        for i in range(3):
            button = QPushButton(f"Label {i+1}")
            button.clicked.connect(self.nothing)
            label_buttons.append(button)
            buttons_layout.addWidget(button)

        main_layout.addLayout(buttons_layout)
        self.setCentralWidget(main_widget)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())