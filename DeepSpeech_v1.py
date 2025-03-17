import wave
import numpy as np
import deepspeech
import librosa
import soundfile as sf
from pydub import AudioSegment
from tqdm import tqdm
import os

def convert_audio(input_file, output_file):
    try:
        audio = AudioSegment.from_mp3(input_file)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_file, format="wav")
    except Exception as e:
        print(f"Conversion failed: {e}")

def trim_silence(input_wav, output_wav):
    y, sr = librosa.load(input_wav, sr=16000)
    yt, _ = librosa.effects.trim(y, top_db=20)
    sf.write(output_wav, yt, sr)

def transcribe_audio(file_path, model_path, scorer_path):
    try:
        model = deepspeech.Model(model_path)
        model.enableExternalScorer(scorer_path)
        with wave.open(file_path, "rb") as audio_file:
            frames = audio_file.getnframes()
            buffer = audio_file.readframes(frames)
            audio = np.frombuffer(buffer, dtype=np.int16)
        return model.stt(audio)
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""

def save_transcription(text, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text)

def process_audio_file(input_mp3, output_folder, model_path, scorer_path):
    temp_wav = os.path.join(output_folder, os.path.basename(input_mp3).replace(".mp3", "_temp.wav"))
    final_wav = os.path.join(output_folder, os.path.basename(input_mp3).replace(".mp3", ".wav"))
    transcript_file = os.path.join(output_folder, os.path.basename(input_mp3).replace(".mp3", ".txt"))

    convert_audio(input_mp3, temp_wav)
    trim_silence(temp_wav, final_wav)
    transcription = transcribe_audio(final_wav, model_path, scorer_path)
    save_transcription(transcription, transcript_file)

    os.remove(temp_wav)

def process_batch(input_folder, output_folder, model_path, scorer_path):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".mp3")]

    for file in tqdm(audio_files, desc="Processing"):
        process_audio_file(file, output_folder, model_path, scorer_path)

def main():
    model_path = input("Enter model file path: ").strip()
    scorer_path = input("Enter scorer file path: ").strip()
    mode = input("Mode (single/batch): ").strip().lower()

    if mode == "single":
        input_mp3 = input("Enter MP3 file path: ").strip()
        output_folder = os.path.dirname(input_mp3)
        process_audio_file(input_mp3, output_folder, model_path, scorer_path)

    elif mode == "batch":
        input_folder = input("Enter folder path: ").strip()
        output_folder = input("Enter output folder path: ").strip()
        process_batch(input_folder, output_folder, model_path, scorer_path)

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()
