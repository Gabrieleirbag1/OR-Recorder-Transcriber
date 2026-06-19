import whisper
import os
from utils import OUTPUT_DIR

def transcribe_audio(file_path, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(file_path)
    return result["text"]

def best_model_test(file_path):
    model_names = ["tiny", "base", "small", "medium"]
    best_model = None
    best_score = float("inf")
    
    for model_name in model_names:
        print(f"Testing model: {model_name}")
        model = whisper.load_model(model_name)
        result = model.transcribe(file_path)
        score = len(result["text"])  # Simple heuristic: shorter transcription might indicate better accuracy
        print(f"Model: {model_name}, Transcription: {result['text']}, Score: {score}")
        
        if score < best_score:
            best_score = score
            best_model = model_name
            
    print(f"Best model: {best_model} with score: {best_score}")

if __name__ == "__main__":
    audio_file = os.path.join(OUTPUT_DIR, "output.wav")
    if os.path.exists(audio_file):
        transcription = transcribe_audio(audio_file, "medium")
        # best_model_test(audio_file)
        print("Transcription:", transcription)
    else:
        print(f"Audio file '{audio_file}' not found. Please record audio first.")