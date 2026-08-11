import os
import json
from shutil import copy as shutil_copy
from litelogging.litelogging import log
from or_recorder_transcriber.utils import CONFIG_PATH, resource_path, DEFAULT_RESSOURCE_LABELS_PATH, DEFAULT_RESSOURCE_MEDICAL_CONTEXT_PATH, DEFAULT_LABELS_PATH, DEFAULT_MEDICAL_CONTEXT_PATH
from or_recorder_transcriber.main_window import MainWindow
from PySide6.QtWidgets import QComboBox, QFileDialog, QGridLayout, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication

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
        self.center_on_screen()  # Center the window on display

    def center_on_screen(self):
        """Center the window on the active primary screen."""
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return
            
        screen_geometry = screen.availableGeometry()
        
        self.adjustSize() 
        window_geometry = self.frameGeometry()
        
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

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

        self.threshold_label = QLabel("Threshold:")
        self.threshold_combobox = QComboBox()
        self.threshold_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        for i in range(101):
            self.threshold_combobox.addItem(str(i / 100.0))
        self.threshold_combobox.setEditable(True)
        self.threshold_combobox.setMaxVisibleItems(10)
        self.threshold_combobox.setCurrentText(str(self.config.get("threshold", 0.75)))

        self.embedding_model_label = QLabel("Embedding Model:")
        self.embedding_model_combobox = QComboBox()
        self.embedding_model_combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.embedding_model_combobox.addItems(["paraphrase-multilingual-mpnet-base-v2", "paraphrase-multilingual-MiniLM-L12-v2"])
        self.embedding_model_browse = QPushButton("Select Embedding Model Directory")
        self.embedding_model_browse.clicked.connect(self.select_directory)
        self.list_embedding_models(self.config.get("embedding_model_dir", ""))
        self.embedding_model_combobox.setCurrentText(self.config.get("embedding_model_name", "paraphrase-multilingual-mpnet-base-v2"))

        self.labels_json_label = QLabel("Labels File (labels.json):")
        self.labels_json_button = QPushButton()
        self._set_file_button_text(self.labels_json_button, self.config.get("labels_json_path", ""), DEFAULT_LABELS_PATH)
        self.labels_json_button.clicked.connect(lambda: self.select_json_file(self.labels_json_button, DEFAULT_LABELS_PATH))

        self.medical_context_json_label = QLabel("Medical Context File (medical_context.json):")
        self.medical_context_json_button = QPushButton()
        self._set_file_button_text(self.medical_context_json_button, self.config.get("medical_context_json_path", ""), DEFAULT_MEDICAL_CONTEXT_PATH)
        self.medical_context_json_button.clicked.connect(lambda: self.select_json_file(self.medical_context_json_button, DEFAULT_MEDICAL_CONTEXT_PATH))

        self.confirm_button = QPushButton("Save" if not self.on_save_close else "Save and Reload Application")
        self.confirm_button.setStyleSheet("QPushButton { margin-top: 12px; }")
        self.confirm_button.clicked.connect(self.on_confirm)

        self.up_layout.addWidget(self.asr_model_label, 0, 0)
        self.up_layout.addWidget(self.asr_model_combobox, 0, 1)
        self.up_layout.addWidget(self.asr_mode_label, 1, 0)
        self.up_layout.addWidget(self.asr_mode_combobox, 1, 1)
        self.up_layout.addWidget(self.language_label, 2, 0)
        self.up_layout.addWidget(self.language_combobox, 2, 1)
        self.up_layout.addWidget(self.threshold_label, 3, 0)
        self.up_layout.addWidget(self.threshold_combobox, 3, 1)

        layout.addWidget(self.up_widget)
        layout.addWidget(self.embedding_model_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.embedding_model_combobox)
        layout.addWidget(self.embedding_model_browse)
        layout.addWidget(self.labels_json_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.labels_json_button)
        layout.addWidget(self.medical_context_json_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.medical_context_json_button)
        layout.addWidget(self.confirm_button)
        self.setCentralWidget(main_widget)

    def _set_file_button_text(self, button: QPushButton, path: str, default_path: str):
        """Set a file-picker button's label to the selected path, or note that the bundled default
        is in use.

        :param button QPushButton: The button whose text to update.
        :param path str: The currently configured path, or an empty string to use the bundled default.
        :param default_path str: The bundled default path to display when `path` is empty."""
        button.setText(f"Selected: {path}" if path else f"Default: {default_path}")

    def _get_button_path(self, button: QPushButton) -> str:
        """Extract the user-selected file path from a file-picker button's text.

        :param button QPushButton: The button to read.

        :return: The selected path, or "" if the bundled default is in use.
        :rtype: str"""
        text = button.text()
        return text.replace("Selected: ", "") if text.startswith("Selected: ") else ""

    def select_json_file(self, button: QPushButton, default_path: str):
        """Open a file dialog to select a JSON file and update the given button's text accordingly.
        If the user cancels, the button keeps its previous selection (or default).

        :param button QPushButton: The button to update with the selected file path.
        :param default_path str: The bundled default path shown if no selection has been made."""
        selected_file, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a JSON File",
            dir="",
            filter="JSON Files (*.json)"
        )
        if selected_file:
            self._set_file_button_text(button, selected_file, default_path)

    def on_confirm(self):
        """Handle the event when the confirm button is clicked, saving the configuration and reloading the main window."""
        asr_model_name = self.asr_model_combobox.currentText()
        embedding_model_name = self.embedding_model_combobox.currentText()
        embedding_model_dir = self.embedding_model_browse.text().replace("Selected: ", "")
        asr_mode = self.asr_mode_combobox.currentText()
        language = self.language_combobox.currentText()
        threshold = self.threshold_combobox.currentText()
        labels_json_path = self._get_button_path(self.labels_json_button)
        medical_context_json_path = self._get_button_path(self.medical_context_json_button)
        log(f"Configuration confirmed: ASR Model: {asr_model_name}, Embedding Model: {embedding_model_name}, ASR Mode: {asr_mode}, Language: {language}, Threshold: {threshold}, Labels: {labels_json_path or 'default'}, Medical Context: {medical_context_json_path or 'default'}", level="DEBUG")
        self.config = {
            "asr_model_name": asr_model_name,
            "embedding_model_name": embedding_model_name,
            "embedding_model_dir": embedding_model_dir,
            "labels_path": labels_json_path,
            "medical_context_path": medical_context_json_path,
            "asr_mode": asr_mode,
            "language": language,
            "threshold": float(threshold),
            "labels_json_path": labels_json_path,
            "medical_context_json_path": medical_context_json_path,
        }
        ConfigManager.update_config(self.config)
        self.close()
        self.closed.emit()
        self.main_window = ConfigManager.load_window(MainWindow, self.theme, self.config)
    
    def list_embedding_models(self, directory: str) -> list[str]:
        """List all embedding models in the specified directory and populate the combobox.
        
        :param directory str: The directory to search for embedding models.
        
        :return: A list of embedding model paths found in the directory.
        :rtype: list[str]"""
        self.embedding_model_browse.setText(f"Selected: {directory}")
        try: 
            models = [os.path.join(os.path.abspath(directory), entry) for entry in os.listdir(directory)]
            for model in models:
                self.embedding_model_combobox.addItem(model)
            return models
        except FileNotFoundError:
            log(f"Directory not found: {directory}", level="ERROR")
            return []
        except PermissionError:
            log(f"Permission denied to access directory: {directory}", level="ERROR")
            return []
        
    def select_directory(self):
        """Open a dialog to select a directory for the embedding model and update the combobox."""
        selected_dir = QFileDialog.getExistingDirectory(
            parent=self, 
            caption="Select a Folder", 
            dir="", 
            options=QFileDialog.Option.ShowDirsOnly
        )
        if selected_dir:
            self.list_embedding_models(selected_dir)

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
        self.__load_assets_files()

    def __load_config(self):
        """Load the configuration from the config.json file, or fall back to default_config.json if necessary."""
        try:
            with open(os.path.join(CONFIG_PATH, "config.json"), "r", encoding="utf-8") as f:
                self.config = json.load(f)
                log(f"Loaded configuration from 'config.json' {os.path.join(CONFIG_PATH, 'config.json')}.", level="DEBUG")
                self.window = self.load_window(MainWindow, self.theme, self.config)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log(f"Error loading config: {e}", level="ERROR")
            try:
                with open(os.path.join(CONFIG_PATH, "default_config.json"), "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                    log("Loaded default configuration.", level="DEBUG")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                log(f"Error loading default config: {e}", level="ERROR")
                default_config_file_local_path = resource_path("config", "default_config.json")
                shutil_copy(default_config_file_local_path, os.path.join(CONFIG_PATH, "default_config.json"))
                with open(os.path.join(CONFIG_PATH, "default_config.json"), "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            self.window = self.load_window(ConfigWindow, self.theme, self.config)
            
    def __load_assets_files(self):
        """Load the default labels and medical context files into the configuration directory if they do not exist."""
        if not os.path.exists(DEFAULT_LABELS_PATH):
            shutil_copy(DEFAULT_RESSOURCE_LABELS_PATH, DEFAULT_LABELS_PATH)
            log("Copied default labels.json to config directory.", level="DEBUG")
        if not os.path.exists(DEFAULT_MEDICAL_CONTEXT_PATH):
            shutil_copy(DEFAULT_RESSOURCE_MEDICAL_CONTEXT_PATH, DEFAULT_MEDICAL_CONTEXT_PATH)
            log("Copied default medical_context.json to config directory.", level="DEBUG")

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