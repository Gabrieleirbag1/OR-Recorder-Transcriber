from recorder import record_until_key_release
import soundfile as sf
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    audio, sr = record_until_key_release()
    print(f"Recording ended. Duration: {len(audio) / sr:.2f} seconds.")
    # save the file 
    sf.write(os.path.join(OUTPUT_DIR, "output.wav"), audio, sr)
    print("File 'output.wav' saved.")
    
if __name__ == "__main__":
    main()
