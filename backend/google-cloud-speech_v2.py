import os
import io
import argparse
from google.cloud import speech
from pydub import AudioSegment

def mp3_to_wav(input_mp3, output_wav):
    try:
        sound = AudioSegment.from_mp3(input_mp3)
        sound = sound.set_channels(1).set_frame_rate(16000)
        sound.export(output_wav, format="wav")
    except Exception as e:
        print(f"Error converting MP3 to WAV: {e}")
        exit(1)

def recognize_speech(wav_path):
    try:
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
        return transcription if transcription else "No transcription available."
    
    except Exception as e:
        print(f"Speech recognition failed: {e}")
        exit(1)

def cleanup_temp_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Could not delete temporary file '{file_path}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert MP3 to text using Google Cloud Speech-to-Text.")
    parser.add_argument("input_file", help="Path to the input MP3 file.")
    
    args = parser.parse_args()
    source_mp3 = args.input_file
    converted_wav = "temp_audio.wav"
    
    if not os.path.exists(source_mp3):
        print(f"Error: File '{source_mp3}' not found.")
        exit(1)

    mp3_to_wav(source_mp3, converted_wav)
    
    print("Transcribing audio...")
    transcription = recognize_speech(converted_wav)
    
    print("\nTranscribed Text:")
    print(transcription)
    
    cleanup_temp_file(converted_wav)

if __name__ == "__main__":
    main()
