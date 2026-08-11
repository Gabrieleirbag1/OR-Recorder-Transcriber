import json
import os
import sys
from platformdirs import user_documents_dir, user_data_dir

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

with open(os.path.join(ASSETS_PATH, "data", "labels.json"), "r", encoding="utf-8") as f:
    EVENT_TYPES = json.load(f)
RAW_LABELS = list(EVENT_TYPES.keys())