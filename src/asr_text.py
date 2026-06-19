import whisper
from utils import OUTPUT_DIR

from nol_event_classifier.supervised.supervised_clustering import match_events_to_labels, RAW_LABELS

def process_audio_to_label(file_path, model_name_asr="base", model_name_embedding="paraphrase-multilingual-mpnet-base-v2"):
    text = transcribe_audio(file_path, model_name_asr)
    print(f"Transcrit : '{text}'")

    if not text:
        return None

    results, _ = match_events_to_labels([text], RAW_LABELS, model_name_embedding, top_k=3)
    return results[0]

def transcribe_audio(file_path, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(file_path)
    return result["text"]

if __name__ == "__main__":
    import os
    audio_file = os.path.join(OUTPUT_DIR, "output.wav")
    if os.path.exists(audio_file):
        result = process_audio_to_label(audio_file, "base")
        print("Résultat de classification:", result)
    else:
        print(f"Audio file '{audio_file}' not found. Please record audio first.")