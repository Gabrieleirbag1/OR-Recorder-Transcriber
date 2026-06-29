import json
import os
import whisper
from lite_logging.lite_logging import log
from utils import OUTPUT_DIR, THRESHOLD
from nol_event_classifier.supervised.supervised_clustering import match_events_to_labels, RAW_LABELS

with open(os.path.join(os.path.dirname(__file__), "medical_context.json"), "r", encoding="utf-8") as f:
    MEDICAL_CONTEXT = ' '.join(json.load(f))

def process_audio_to_label(file_path, model_name_asr="base", model_name_embedding="paraphrase-multilingual-mpnet-base-v2"):
    text = transcribe_audio(file_path, model_name_asr)
    log(f"Transcribed : '{text}'")

    if not text:
        return None

    results, _ = match_events_to_labels([text], RAW_LABELS, model_name_embedding, top_k=3)
    log("Classification results: " + str(results[0]))
    return results[0]

def transcribe_audio(file_path, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(file_path, initial_prompt=MEDICAL_CONTEXT)
    return result["text"]

def handle_label_selection(result):
    best_score = float(result["best_score"])
    if best_score:
        print("Please select the most appropriate label from the following options:")
        for (i, event) in enumerate(result["top_k"]):
            print(f"[{i+1}] Label: {event['label']}, Score: {event['score']}")
        else:
            input_str = input("Enter the number of the selected label (or press Enter to skip): ")
            if input_str.strip().isdigit():
                selected_index = int(input_str.strip()) - 1
                if 0 <= selected_index < len(result["top_k"]):
                    selected_label = result["top_k"][selected_index]
                    log(f"User selected label: {selected_label}")
                    return selected_label
                else:
                    log("Invalid selection. No label selected.")
            else:
                log("No label selected by user.")
    return result["top_k"][0]

def evaluate_audio_label(file_path, model_name_asr="base", model_name_embedding="paraphrase-multilingual-mpnet-base-v2"):
    result = process_audio_to_label(file_path, model_name_asr, model_name_embedding)
    if result is None:
        log("Unable to classify audio. Please try again.")
        return None

    best_label = handle_label_selection(result)
    return best_label

if __name__ == "__main__":
    import os
    audio_file = os.path.join(OUTPUT_DIR, "output.wav")
    if os.path.exists(audio_file):
        result = evaluate_audio_label(audio_file, "tiny")
        log(f"Best label: {result['label']} (score: {result['score']:.2f})")
    else:
        log(f"Audio file '{audio_file}' not found. Please record audio first.", level="ERROR")