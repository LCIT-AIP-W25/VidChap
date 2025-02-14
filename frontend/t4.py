# 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

import openai
import numpy as np
import os
import json
import wave
import vosk
import subprocess
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
openai.api_key = "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"


def convert_mp3_to_wav(mp3_file: str) -> str:
    """Convert MP3 file to WAV format using ffmpeg."""
    logger.info(f"Converting MP3 file '{mp3_file}' to WAV format...")
    
    wav_file = mp3_file.replace(".mp3", ".wav")
    command = [
        "ffmpeg", "-i", mp3_file, "-ac", "1", "-ar", "16000",
        "-sample_fmt", "s16", wav_file
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        error_msg = f"FFmpeg conversion failed: {result.stderr.decode()}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    return wav_file  # Return the path to the converted WAV file

def transcribe_audio_vosk(audio_path, model_path="vosk-model"):
    """Transcribes an audio file using Vosk ASR."""
    if not os.path.exists(model_path):
        raise ValueError("Vosk model not found! Download and extract it first.")

    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise ValueError("Audio file must be WAV format with PCM encoding")

    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, wf.getframerate())

    transcript = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if "text" in result:
                transcript.append({"text": result["text"], "start": wf.tell() / wf.getframerate()})

    wf.close()
    return transcript

def llm_format_transcript(raw_text):
    """Use an LLM to structure transcript into paragraphs."""
    prompt = f"Structure the following transcript into readable paragraphs:\n\n{raw_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

def reassign_timestamps(original_transcript, formatted_transcript):
    """Use TF-IDF to map structured paragraphs back to timestamps."""
    raw_texts = [item["text"] for item in original_transcript]
    raw_timestamps = [item["start"] for item in original_transcript]

    vectorizer = TfidfVectorizer()
    raw_matrix = vectorizer.fit_transform(raw_texts)
    formatted_sentences = formatted_transcript.split("\n")
    formatted_matrix = vectorizer.transform(formatted_sentences)

    timestamps = []
    for sentence_vector in formatted_matrix:
        similarities = cosine_similarity(sentence_vector, raw_matrix).flatten()
        best_match_idx = np.argmax(similarities)
        timestamps.append(raw_timestamps[best_match_idx])

    return [{"text": sentence, "timestamp": ts} for sentence, ts in zip(formatted_sentences, timestamps)]

def generate_chapter_titles(structured_transcript):
    """Use an LLM to generate chapter titles."""
    transcript_text = "\n".join([f"{item['timestamp']}: {item['text']}" for item in structured_transcript])
    prompt = f"Segment this transcript into chapters and provide titles:\n\n{transcript_text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Example usage
input_audio = "a2.mp3"  # Can be MP3 or WAV
vosk_model_path = "vosk-model-small-en-us-0.15"

# Convert MP3 to WAV if necessary
if input_audio.endswith(".mp3"):
    input_audio = convert_mp3_to_wav(input_audio)

raw_transcript = transcribe_audio_vosk(input_audio, vosk_model_path)

# Convert transcript list into text
raw_text = " ".join([item["text"] for item in raw_transcript])

formatted_text = llm_format_transcript(raw_text)
structured_transcript = reassign_timestamps(raw_transcript, formatted_text)
chapter_titles = generate_chapter_titles(structured_transcript)

print("\nChapters with Titles:\n", chapter_titles)
