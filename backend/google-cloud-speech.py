import io
import os
from google.cloud import speech
from pydub import AudioSegment

# Set up Google Cloud credentials (Download credentials.json from Google Cloud Console)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

def convert_mp3_to_wav(mp3_file, wav_file):
    """
    Converts MP3 file to WAV format (16kHz mono) using pydub.
    """
    audio = AudioSegment.from_mp3(mp3_file)
    audio = audio.set_channels(1).set_frame_rate(16000)  # Mono, 16kHz sample rate
    audio.export(wav_file, format="wav")

def transcribe_audio(wav_file):
    """
    Transcribes the WAV file using Google Cloud Speech-to-Text API.
    """
    client = speech.SpeechClient()

    with io.open(wav_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_word_time_offsets=True,  # Adds timestamps to words
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "

    return transcript.strip()

def main():
    # Define file paths
    mp3_file = "audio.mp3"  
    wav_file = "audio.wav"

    # Convert MP3 to WAV
    convert_mp3_to_wav(mp3_file, wav_file)
    print("MP3 converted to WAV.")

    # Transcribe the audio
    transcript = transcribe_audio(wav_file)
    print("\n Transcription:")
    print(transcript)

    os.remove(wav_file)
    print(" Temporary WAV file deleted.")

if __name__ == "__main__":
    main()
