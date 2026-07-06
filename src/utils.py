import os

THRESHOLD = 0.75

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)