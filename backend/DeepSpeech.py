import wave
import numpy as np
import deepspeech
import librosa
import soundfile as sf
from pydub import AudioSegment
from tqdm import tqdm
import os

# Paths to DeepSpeech model and scorer (download separately)
MODEL_PATH = "deepspeech-0.9.3-models.pbmm"
SCORER_PATH = "deepspeech-0.9.3-models.scorer"
LOG_FILE = "transcription_log.txt"

def convert_audio(input_file, output_file):
    """Converts MP3 to WAV format suitable for DeepSpeech."""
    try:
        print("[INFO] Converting MP3 to WAV...")
        audio = AudioSegment.from_mp3(input_file)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_file, format="wav")
        print("[SUCCESS] Conversion Complete.")
    except Exception as e:
        print(f"[ERROR] Audio conversion failed: {e}")

def trim_silence(input_wav, output_wav):
    """Removes silent parts from the beginning and end of an audio file."""
    print("[INFO] Trimming silence from audio...")
    y, sr = librosa.load(input_wav, sr=16000)
    yt, _ = librosa.effects.trim(y, top_db=20)  # Trim silence
    sf.write(output_wav, yt, sr)
    print("[SUCCESS] Silence trimmed.")

def transcribe_audio(file_path):
    """Transcribes audio using Mozilla DeepSpeech."""
    try:
        model = deepspeech.Model(MODEL_PATH)
        model.enableExternalScorer(SCORER_PATH)

        with wave.open(file_path, "rb") as audio_file:
            frames = audio_file.getnframes()
            buffer = audio_file.readframes(frames)
            audio = np.frombuffer(buffer, dtype=np.int16)

        print("[INFO] Transcribing audio...")
        text = model.stt(audio)
        return text
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return ""

def save_transcription(text, output_file):
    """Saves transcription text to a file."""
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"[SUCCESS] Transcription saved to {output_file}")

def process_multiple_audios(input_folder, output_folder):
    """Processes multiple MP3 files in a folder and transcribes them."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_files = [f for f in os.listdir(input_folder) if f.endswith(".mp3")]
    
    if not audio_files:
        print("[INFO] No MP3 files found in the folder.")
        return

    for file in tqdm(audio_files, desc="Processing Files"):
        input_mp3 = os.path.join(input_folder, file)
        temp_wav = os.path.join(output_folder, file.replace(".mp3", "_temp.wav"))
        final_wav = os.path.join(output_folder, file.replace(".mp3", ".wav"))
        transcript_file = os.path.join(output_folder, file.replace(".mp3", ".txt"))

        convert_audio(input_mp3, temp_wav)
        trim_silence(temp_wav, final_wav)

        transcription = transcribe_audio(final_wav)
        save_transcription(transcription, transcript_file)

        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"{file}: {transcription}\n")

        os.remove(temp_wav)  # Clean up temporary file

    print(f"[INFO] Processed {len(audio_files)} files successfully.")

def main():
    """Main function to run transcription on a single file or batch process."""
    mode = input("Enter mode (single/batch): ").strip().lower()

    if mode == "single":
        input_mp3 = input("Enter the path to the MP3 file: ").strip()
        output_wav = input_mp3.replace(".mp3", ".wav")
        transcript_output = input_mp3.replace(".mp3", ".txt")

        convert_audio(input_mp3, output_wav)
        trim_silence(output_wav, output_wav)

        transcription = transcribe_audio(output_wav)
        save_transcription(transcription, transcript_output)

    elif mode == "batch":
        input_folder = input("Enter the folder containing MP3 files: ").strip()
        output_folder = input("Enter the output folder: ").strip()
        process_multiple_audios(input_folder, output_folder)

    else:
        print("[ERROR] Invalid mode selected. Choose 'single' or 'batch'.")

if __name__ == "__main__":
    main()
