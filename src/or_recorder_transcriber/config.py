import os
import json
from lite_logging.lite_logging import log
from or_recorder_transcriber.utils import CONFIG_PATH
from or_recorder_transcriber.main_window import MainWindow
from PySide6.QtWidgets import QComboBox, QFileDialog, QGridLayout, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

class ConfigWindow(QMainWindow):
    """A window for configuring application settings such as ASR model, embedding model, and language.
    
    :param theme str: The theme of the window (light or dark).
    :param config dict: The current configuration settings.
    :param on_save_close bool: Whether to close the window after saving the configuration.
    """
    closed = Signal()

    def __init__(self, theme: str = "light", config: dict[str, str] = None, on_save_close: bool = False):
        """Initialize the ConfigWindow with the given theme and configuration.
        
        :param theme str: The theme of the window (light or dark).
        :param config dict: The current configuration settings.
        :param on_save_close bool: Whether to close the window after saving the configuration."""
        super().__init__()
        self.theme = theme
        self.config = config
        self.on_save_close = on_save_close

        self.main_window = None
        
        self.setup()

    def setup(self):
        """Set up the configuration window UI."""
        self.setWindowTitle("Configuration")
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface elements for the configuration window."""
        layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.up_layout = QGridLayout()
        self.up_widget = QWidget()
        self.up_widget.setLayout(self.up_layout)

        self.asr_model_label = QLabel("ASR Model:")
        self.asr_model_combobox = QComboBox()
        self.asr_model_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.asr_model_combobox.addItems(["tiny", "base", "small", "medium", "large"])
        self.asr_model_combobox.setCurrentText(self.config.get("asr_model_name", "tiny"))

        self.asr_mode_label = QLabel("ASR Mode:")
        self.asr_mode_combobox = QComboBox()
        self.asr_mode_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.asr_mode_combobox.addItems(["faster_whisper", "whisper", "pywhispercpp"])
        self.asr_mode_combobox.setCurrentText(self.config.get("asr_mode", "faster_whisper"))

        self.language_label = QLabel("Language:")
        self.language_combobox = QComboBox()
        self.language_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.language_combobox.addItems(["fr", "en", "es", "de", "it", "pt", "nl", "ru", "zh"])
        self.language_combobox.setCurrentText(self.config.get("language", "fr"))
        
        self.embedding_model_label = QLabel("Embedding Model:")
        self.embedding_model_combobox = QComboBox()
        self.embedding_model_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.embedding_model_combobox.addItems(["paraphrase-multilingual-mpnet-base-v2"])
        if self.config.get("embedding_model_name") and self.config.get("embedding_model_name") not in ["paraphrase-multilingual-mpnet-base-v2"]:
            self.embedding_model_combobox.addItem(self.config.get("embedding_model_name").split("/")[-1])
        self.embedding_model_combobox.setCurrentText(self.config.get("embedding_model_name", "paraphrase-multilingual-mpnet-base-v2"))
        self.embedding_model_browse = QPushButton("Select Embedding Model Directory")
        self.embedding_model_browse.clicked.connect(self.select_directory)

        self.confirm_button = QPushButton("Save" if not self.on_save_close else "Save and Reload Application")
        self.confirm_button.setStyleSheet("QPushButton { margin-top: 12px; }")
        self.confirm_button.clicked.connect(self.on_confirm)

        self.up_layout.addWidget(self.asr_model_label, 0, 0)
        self.up_layout.addWidget(self.asr_model_combobox, 0, 1)
        self.up_layout.addWidget(self.asr_mode_label, 1, 0)
        self.up_layout.addWidget(self.asr_mode_combobox, 1, 1)
        self.up_layout.addWidget(self.language_label, 2, 0)
        self.up_layout.addWidget(self.language_combobox, 2, 1)

        layout.addWidget(self.up_widget)
        layout.addWidget(self.embedding_model_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.embedding_model_combobox)
        layout.addWidget(self.embedding_model_browse)
        layout.addWidget(self.confirm_button)
        self.setCentralWidget(main_widget)

    def on_confirm(self):
        """Handle the event when the confirm button is clicked, saving the configuration and reloading the main window."""
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
        self.closed.emit()
        self.main_window = ConfigManager.load_window(MainWindow, self.theme, self.config)

    def select_directory(self):
        """Open a dialog to select a directory for the embedding model and update the combobox."""
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
    """Manage the configuration settings for the application, including loading and saving configurations.
    
    :param theme str: The theme of the application (light or dark).
    """
    def __init__(self, theme: str = "light"):
        """Initialize the ConfigManager with the given theme.
        
        :param theme str: The theme of the application (light or dark)."""
        self.theme = theme

        self.config = None
        self.window = None

        self.__load_config()

    def __load_config(self):
        """Load the configuration from the config.json file, or fall back to default_config.json if necessary."""
        try:
            with open(os.path.join(CONFIG_PATH, "config.json"), "r", encoding="utf-8") as f:
                self.config = json.load(f)
                log("Loaded configuration from 'config.json'.", level="DEBUG")
                self.window = self.load_window(MainWindow, self.theme, self.config)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log(f"Error loading config: {e}", level="ERROR")
            with open(os.path.join(CONFIG_PATH, "default_config.json"), "r", encoding="utf-8") as f:
                self.config = json.load(f)
                log("Loaded default configuration.", level="DEBUG")
            self.window = self.load_window(ConfigWindow, self.theme, self.config)

    @staticmethod
    def update_config(new_config: dict[str, str]):
        """Update the configuration settings and save them to the config.json file.

        :param new_config dict: The new configuration settings to be saved."""
        with open(os.path.join(CONFIG_PATH, "config.json"), "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=4)
        log("Configuration updated and saved to 'config.json'.", level="DEBUG")

    @staticmethod
    def load_window(window: MainWindow | ConfigWindow, theme: str, config: dict[str, str]) -> MainWindow | ConfigWindow:
        """Load the specified window (MainWindow or ConfigWindow) with the given theme and configuration.

        :param window MainWindow | ConfigWindow: The window class to be loaded.
        :param theme str: The theme of the window (light or dark).
        :param config dict: The configuration settings to be passed to the window.
        
        :return: An instance of the specified window class.
        :rtype: MainWindow | ConfigWindow
        """
        window_instance = ConfigWindow(theme, config) if window == ConfigWindow else MainWindow(config, theme)
        window_instance.show()
        return window_instance