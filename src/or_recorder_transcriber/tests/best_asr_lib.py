import whisper
import faster_whisper
from pywhispercpp.model import Model
import time
import os
from lite_logging.lite_logging import log

file_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "output", "audio", "output_copy.wav")
print(os.path.abspath(file_path))


# --- LOADING FUNCTIONS ---

def load_whisper_model(model_name="base"):
    model = whisper.load_model(model_name)
    log(f"Whisper model '{model_name}' loaded.")
    return model

def load_faster_whisper_model(model_name="base"):
    model = faster_whisper.WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
        cpu_threads=4
    )
    log(f"Faster Whisper model '{model_name}' loaded.")
    return model

def load_pywhispercpp_model(model_name="base"):
    # Note : On force l'utilisation de model_name passé en paramètre
    model = Model(model_name, n_threads=4)
    log(f"PyWhisperCpp model '{model_name}' loaded.")
    return model


# --- TRANSCRIPTION FUNCTIONS (Modified to return (text, time)) ---

def transcribe_whisper_audio(file_path, model):
    chronomètre = time.time()
    result = model.transcribe(file_path, language="fr")
    elapsed = time.time() - chronomètre
    log(f"Audio processed in {elapsed:.2f} seconds.")
    return result["text"].strip(), elapsed

def transcribe_faster_whisper_audio(file_path, model):
    chronomètre = time.time()
    segments, info = model.transcribe(
        file_path,
        language="fr",
        beam_size=1,
    )
    elapsed = time.time() - chronomètre
    text = " ".join(segment.text for segment in segments).strip()
    log(f"Audio processed in {elapsed:.2f} seconds.")
    return text, elapsed

def transcribe_pywhispercpp_audio(file_path, model):
    chronomètre = time.time()
    result = model.transcribe(file_path, language="fr")
    elapsed = time.time() - chronomètre
    text = result[0].text.strip() if result else ""
    log(f"Audio processed in {elapsed:.2f} seconds.")
    return text, elapsed


# --- TABLE RENDERING FUNCTION ---

def print_summary_table(results):
    """Generate and print a neat summary table to the console."""
    # Column widths: Model (10), Engine (16), Time (12), Transcription (50)
    header = f"| {'Modèle':<10} | {'Moteur':<16} | {'Temps (s)':<10} | {'Transcription (extrait)':<45} |"
    separator = "+" + "-"*12 + "+" + "-"*18 + "+" + "-"*12 + "+" + "-"*47 + "+"
    
    print("\n" + separator)
    print(header)
    print(separator)
    
    for r in results:
        # Truncate the transcription if it's too long for the table
        raw_text = r['text'].replace('\n', ' ')
        text_preview = raw_text if len(raw_text) <= 42 else raw_text[:42] + "..."
        
        print(f"| {r['model']:<10} | {r['engine']:<16} | {r['time']:<10.2f} | {text_preview:<45} |")
        
    print(separator + "\n")


# --- MAIN LOOP ---

# List to store result dictionaries
all_results = []

for model_name in ["tiny", "base"]:
    log(f"--- EVALUATING MODEL : {model_name.upper()} ---")
    
    # 1. OpenAI Whisper
    whisper_model = load_whisper_model(model_name)
    txt_w, time_w = transcribe_whisper_audio(file_path, whisper_model)
    all_results.append({"model": model_name, "engine": "Whisper", "time": time_w, "text": txt_w})
    log(f"Whisper transcription result: {txt_w}")

    # 2. Faster Whisper
    faster_whisper_model = load_faster_whisper_model(model_name)
    txt_fw, time_fw = transcribe_faster_whisper_audio(file_path, faster_whisper_model)
    all_results.append({"model": model_name, "engine": "Faster Whisper", "time": time_fw, "text": txt_fw})
    log(f"Faster Whisper transcription result: {txt_fw}")

    # 3. PyWhisperCpp
    pywhispercpp_model = load_pywhispercpp_model(model_name)
    txt_pw, time_pw = transcribe_pywhispercpp_audio(file_path, pywhispercpp_model)
    all_results.append({"model": model_name, "engine": "PyWhisperCpp", "time": time_pw, "text": txt_pw})
    log(f"PyWhisperCpp transcription result: {txt_pw}")

# Affichage du tableau final
print_summary_table(all_results)