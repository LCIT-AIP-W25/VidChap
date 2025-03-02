import os
import io
from google.cloud import speech
from pydub import AudioSegment

# Configure Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

def mp3_to_wav(input_mp3, output_wav):
    """
    Converts an MP3 file to WAV format (mono, 16kHz) using pydub.
    """
    sound = AudioSegment.from_mp3(input_mp3)
    sound = sound.set_channels(1).set_frame_rate(16000)
    sound.export(output_wav, format="wav")

def recognize_speech(wav_path):
    """
    Processes the WAV file with Google Cloud Speech-to-Text API.
    """
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
    
    return " ".join(result.alternatives[0].transcript for result in response.results)

def run():
    source_mp3 = "audio.mp3"
    converted_wav = "converted_audio.wav"
    
    mp3_to_wav(source_mp3, converted_wav)
    print("Audio conversion complete.")
    
    transcription = recognize_speech(converted_wav)
    print("\nTranscribed Text:")
    print(transcription)
    
    os.remove(converted_wav)
    print("Temporary file removed.")

if __name__ == "__main__":
    run()
