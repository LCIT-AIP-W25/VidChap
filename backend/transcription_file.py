import os
import subprocess
import json
import io
import logging
import argparse
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment


# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert_mp3_to_wav_with_ffmpeg(mp3_file, sample_rate=16000):
    """Convert MP3 file to WAV format using ffmpeg."""
    try:
        logging.info(f"Converting MP3 file '{mp3_file}' to WAV...")
        command = [
            "ffmpeg", "-i", mp3_file, "-ac", "1", "-ar", str(sample_rate),
            "-sample_fmt", "s16", "-f", "wav", "pipe:1"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            raise Exception(f"Error during MP3 to WAV conversion: {result.stderr.decode()}")

        return result.stdout
    except Exception as e:
        logging.error(f"Error during conversion: {e}")
        raise


def recognize_speech_in_chunks(audio_data, model_path, chunk_duration=10000):
    """Recognize speech in chunks using Vosk."""
    try:
        logging.info("Loading Vosk model...")
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)

        audio = AudioSegment.from_wav(io.BytesIO(audio_data))
        data = []

        # Process each 10-second chunk
        for i in range(0, len(audio), chunk_duration):
            chunk = audio[i:i + chunk_duration]
            audio_data_chunk = chunk_to_audio_data(chunk)

            # Feed the audio chunk to the recognizer
            if recognizer.AcceptWaveform(audio_data_chunk):
                result = recognizer.Result()
                result_dict = json.loads(result)
                timestamp = i / 1000  # Convert milliseconds to seconds
                info = f"Timestamp: {timestamp:.2f}s - Text: {result_dict.get('text', '')}"
                logging.info(info)
                data.append(info)

        # Return the transcriptions collected in all chunks
        return data
    except Exception as e:
        logging.error(f"Error during speech recognition: {e}")
        return []


def chunk_to_audio_data(chunk):
    """Convert an audio chunk to byte data."""
    with io.BytesIO() as buffer:
        chunk.export(buffer, format="wav")
        buffer.seek(0)
        return buffer.read()


def main():
    parser = argparse.ArgumentParser(description="Convert MP3 to text using Vosk.")
    parser.add_argument("mp3_file", help="Path to the input MP3 file.")
    parser.add_argument("model_path", help="Path to the Vosk model directory.")
    parser.add_argument("--chunk_duration", type=int, default=10000, help="Duration of audio chunks in milliseconds (default: 10000).")
    args = parser.parse_args()

    mp3_file = args.mp3_file
    model_path = args.model_path
    chunk_duration = args.chunk_duration

    # Check if MP3 file exists
    if not os.path.exists(mp3_file):
        logging.error(f"MP3 file '{mp3_file}' not found.")
        return

    # Check if Vosk model path exists
    if not os.path.exists(model_path):
        logging.error(f"Vosk model '{model_path}' not found.")
        return

    try:
        # Convert MP3 to WAV in memory
        audio_data = convert_mp3_to_wav_with_ffmpeg(mp3_file)
        
        # Recognize speech in chunks
        transcription_data = recognize_speech_in_chunks(audio_data, model_path, chunk_duration)
        
        if transcription_data:
            logging.info("Final Transcription:")
            print("\n".join(transcription_data))
        else:
            logging.info("No transcription data available.")
    except Exception as e:
        logging.error(f"Processing failed: {e}")


if __name__ == "__main__":
    main()
