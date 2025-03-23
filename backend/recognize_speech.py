import os
import io
import argparse
import logging
from google.cloud import speech
from pydub import AudioSegment
from time import time
import tempfile


# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpeechRecognitionError(Exception):
    pass


class FileConversionError(Exception):
    pass


def mp3_to_wav(input_mp3, output_wav, channels=1, sample_rate=16000):
    """Convert an MP3 file to WAV format with given channel and sample rate options."""
    try:
        logging.info(f"Converting {input_mp3} to WAV...")
        sound = AudioSegment.from_mp3(input_mp3)
        sound = sound.set_channels(channels).set_frame_rate(sample_rate)
        sound.export(output_wav, format="wav")
        logging.info(f"Conversion successful: {output_wav}")
    except Exception as e:
        raise FileConversionError(f"Error converting MP3 to WAV: {e}")


def recognize_speech(wav_path):
    """Recognize speech from the given WAV file using Google Cloud Speech-to-Text."""
    try:
        logging.info(f"Starting speech recognition on {wav_path}...")
        client = speech.SpeechClient()

        with io.open(wav_path, "rb") as audio_file:
            audio_data = audio_file.read()

        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_word_time_offsets=True,
        )

        response = client.recognize(config=config, audio=audio)
        transcription = " ".join(result.alternatives[0].transcript for result in response.results)
        logging.info(f"Transcription completed.")
        return transcription if transcription else "No transcription available."
    
    except Exception as e:
        raise SpeechRecognitionError(f"Speech recognition failed: {e}")


def cleanup_temp_file(file_path):
    """Clean up temporary files after processing."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Successfully deleted temporary file: {file_path}")
    except Exception as e:
        logging.warning(f"Could not delete temporary file '{file_path}': {e}")


def process_mp3_files(mp3_files):
    """Process a list of MP3 files and transcribe them."""
    transcriptions = {}

    for mp3_file in mp3_files:
        temp_wav = tempfile.mktemp(suffix='.wav')
        
        try:
            mp3_to_wav(mp3_file, temp_wav)
            transcription = recognize_speech(temp_wav)
            transcriptions[mp3_file] = transcription
        except (FileConversionError, SpeechRecognitionError) as e:
            logging.error(f"Error processing {mp3_file}: {e}")
        finally:
            cleanup_temp_file(temp_wav)
    
    return transcriptions


def main():
    parser = argparse.ArgumentParser(description="Convert MP3 to text using Google Cloud Speech-to-Text.")
    parser.add_argument("input_files", nargs='+', help="Paths to input MP3 files.")
    
    args = parser.parse_args()
    input_files = args.input_files

    for mp3_file in input_files:
        if not os.path.exists(mp3_file):
            logging.error(f"Error: File '{mp3_file}' not found.")
            continue

    start_time = time()
    transcriptions = process_mp3_files(input_files)
    
    logging.info("Transcription results:")
    for file, transcription in transcriptions.items():
        logging.info(f"{file}: {transcription[:100]}...")  # Show only the first 100 chars for preview

    elapsed_time = time() - start_time
    logging.info(f"Completed processing {len(input_files)} files in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
