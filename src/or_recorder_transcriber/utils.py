import json
import os
import sys
from platformdirs import user_documents_dir, user_data_dir
from litelogging.litelogging import log

def resource_path(*parts: str) -> str:
    """Resolve a path to a bundled resource, working both in dev and in a PyInstaller onefile build.

    :param *parts: Path components to join.

    :return: The resolved absolute path to the resource.
    :rtype: str"""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, *parts)

ASSETS_PATH = resource_path("assets")

CONFIG_PATH = os.path.join(user_data_dir(), "ORRT", "config")

OUTPUT_DIR = os.path.join(user_documents_dir(), "ORRT")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")

os.makedirs(CONFIG_PATH, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

DEFAULT_RESSOURCE_LABELS_PATH = os.path.join(resource_path("config", "default_labels.json"))
DEFAULT_RESSOURCE_MEDICAL_CONTEXT_PATH = os.path.join(resource_path("config", "default_medical_context.json"))
DEFAULT_LABELS_PATH = os.path.join(CONFIG_PATH, "default_labels.json")
DEFAULT_MEDICAL_CONTEXT_PATH = os.path.join(CONFIG_PATH, "default_medical_context.json")

def _load_json_with_fallback(path: str | None, default_path: str, description: str):
    """Load JSON from `path`, falling back to `default_path` if `path` is empty, missing, or not
    valid JSON. If `default_path` itself fails to load, the exception is raised since there is
    nothing left to fall back to.

    :param path str | None: The user-selected path to try first, or None/empty to skip straight to the default.
    :param default_path str: The bundled default path to fall back to.
    :param description str: A human-readable description of what is being loaded, for log messages.

    :return: The parsed JSON content.
    :rtype: Any"""
    candidate = path if path else default_path
    try:
        with open(candidate, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if candidate == default_path:
            raise
        log(f"Could not load {description} from '{candidate}': {e}. Falling back to bundled default.", level="WARNING")
        with open(default_path, "r", encoding="utf-8") as f:
            return json.load(f)

def load_labels(path: str | None = None) -> dict:
    """Load the Event Type label mapping (label -> "Medication"/"Other") from the given JSON file,
    falling back to the bundled default file if the given path is missing, unreadable, or invalid.
    Passing None (or an empty string) uses the bundled default directly.

    :param path str | None: Path to a user-selected labels.json file, or None to use the bundled default.

    :return: The label mapping loaded from disk.
    :rtype: dict"""
    return _load_json_with_fallback(path, DEFAULT_RESSOURCE_LABELS_PATH, "labels")

def load_medical_context(path: str | None = None) -> str:
    """Load the medical context prompt (a list of terms joined into a single string used as the ASR
    initial prompt) from the given JSON file, falling back to the bundled default file if the given
    path is missing, unreadable, or invalid. Passing None (or an empty string) uses the bundled
    default directly.

    :param path str | None: Path to a user-selected medical_context.json file, or None to use the bundled default.

    :return: The medical context terms joined into a single space-separated string.
    :rtype: str"""
    data = _load_json_with_fallback(path, DEFAULT_RESSOURCE_MEDICAL_CONTEXT_PATH, "medical context")
    return ' '.join(data)