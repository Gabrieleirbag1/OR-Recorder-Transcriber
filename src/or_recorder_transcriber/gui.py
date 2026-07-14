from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from or_recorder_transcriber.config import ConfigManager
import sys

def main():
    app = QApplication(sys.argv)
    theme = "dark" if app.styleHints().colorScheme() == Qt.ColorScheme.Dark else "light"
    config_manager = ConfigManager(theme)
    sys.exit(app.exec())