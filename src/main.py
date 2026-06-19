from recorder import record_until_key_release
import soundfile as sf
import os

from utils import OUTPUT_DIR

def main():
    audio, sr = record_until_key_release()
    print(f"Recording ended. Duration: {len(audio) / sr:.2f} seconds.")
    # save the file 
    sf.write(os.path.join(OUTPUT_DIR, "output.wav"), audio, sr)
    print("File 'output.wav' saved.")
    
if __name__ == "__main__":
    main()
