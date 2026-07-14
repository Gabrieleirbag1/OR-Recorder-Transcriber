    

import os
import json
from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import CONFIG_PATH
from or_recorder_transcriber.main_window import MainWindow
from PySide6.QtWidgets import QComboBox, QFileDialog, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ConfigWindow(QMainWindow):
    def __init__(self, theme="light", config=None):
        super().__init__()
        self.theme = theme
        self.config = config
        
        self.setup()

    def setup(self):
        self.setWindowTitle("Configuration")
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.asr_model_label = QLabel("ASR Model:")
        self.asr_model_combobox = QComboBox()
        self.asr_model_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.asr_model_combobox.addItems(["tiny", "base", "small", "medium", "large"])

        self.embedding_model_label = QLabel("Embedding Model:")
        self.embedding_model_combobox = QComboBox()
        self.embedding_model_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.embedding_model_combobox.addItems(["paraphrase-multilingual-mpnet-base-v2"])
        self.embedding_model_browse = QPushButton("Select Embedding Model Directory")
        self.embedding_model_browse.clicked.connect(self.select_directory)

        self.asr_mode_label = QLabel("ASR Mode:")
        self.asr_mode_combobox = QComboBox()
        self.asr_mode_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.asr_mode_combobox.addItems(["faster_whisper", "whisper", "pywhispercpp"])

        self.language_label = QLabel("Language:")
        self.language_combobox = QComboBox()
        self.language_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.language_combobox.addItems(["fr", "en", "es", "de", "it", "pt", "nl", "ru", "zh"])

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.on_confirm)

        layout.addWidget(self.asr_model_label)
        layout.addWidget(self.asr_model_combobox)
        layout.addWidget(self.embedding_model_label)
        layout.addWidget(self.embedding_model_combobox)
        layout.addWidget(self.embedding_model_browse)
        layout.addWidget(self.asr_mode_label)
        layout.addWidget(self.asr_mode_combobox)
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_combobox)
        layout.addWidget(self.confirm_button)
        self.setCentralWidget(main_widget)

    def on_confirm(self):
        asr_model_name = self.asr_model_combobox.currentText()
        embedding_model_name = self.embedding_model_combobox.currentText()
        asr_mode = self.asr_mode_combobox.currentText()
        language = self.language_combobox.currentText()
        log(f"Configuration confirmed: ASR Model: {asr_model_name}, Embedding Model: {embedding_model_name}, ASR Mode: {asr_mode}, Language: {language}", level="DEBUG")
        self.config = {
            "asr_model_name": asr_model_name,
            "embedding_model_name": embedding_model_name,
            "asr_mode": asr_mode,
            "language": language
        }
        ConfigManager.update_config(self.config)
        self.close()
        window = ConfigManager.load_window(MainWindow, self.theme, self.config)

    def select_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(
            parent=self, 
            caption="Select a Folder", 
            dir="", 
            options=QFileDialog.Option.ShowDirsOnly
        )
        
        if selected_dir:
            self.embedding_model_combobox.addItem(selected_dir)
            self.embedding_model_combobox.setCurrentText(selected_dir)

class ConfigManager:
    def __init__(self, theme):
        self.config = None
        self.theme = theme

        self.__load_config()

    def __load_config(self):
        try:
            with open(os.path.join(CONFIG_PATH, "config.json"), "r", encoding="utf-8") as f:
                self.config = json.load(f)
                log("Loaded configuration from 'config.json'.", level="DEBUG")
                window = self.load_window(MainWindow, self.theme, self.config)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log(f"Error loading config: {e}", level="ERROR")
            with open(os.path.join(CONFIG_PATH, "default_config.json"), "r", encoding="utf-8") as f:
                self.config = json.load(f)
                log("Loaded default configuration.", level="DEBUG")
            window = self.load_window(ConfigWindow, self.theme, self.config)

    @staticmethod
    def update_config(new_config):
        with open(os.path.join(CONFIG_PATH, "config.json"), "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=4)
        log("Configuration updated and saved to 'config.json'.", level="DEBUG")

    @staticmethod
    def load_window(window: MainWindow | ConfigWindow, theme, config):
        window_instance = ConfigWindow(theme, config) if window == ConfigWindow else MainWindow(config, theme)
        window_instance.show()
        return window_instance