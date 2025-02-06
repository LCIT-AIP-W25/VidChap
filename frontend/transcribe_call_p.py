import numpy as np
import concurrent.futures
from vosk import Model, KaldiRecognizer
import wave
import json

# Function to split audio into chunks
def split_audio(wav_data, chunk_size_ms=10000, sr=16000):
    # Convert the chunk size from milliseconds to samples
    chunk_size_samples = int(chunk_size_ms * sr / 1000)
    chunks = []

    # Split the wav_data into chunks
    for start in range(0, len(wav_data), chunk_size_samples):
        end = min(start + chunk_size_samples, len(wav_data))
        chunks.append(wav_data[start:end])

    return chunks

# Function to transcribe a single chunk
def transcribe_chunk(chunk, model, sr=16000):
    # Create a recognizer
    recognizer = KaldiRecognizer(model, sr)
    
    # Feed the chunk into the recognizer
    recognizer.AcceptWaveform(chunk)
    
    # Return the transcription result
    result = json.loads(recognizer.Result())
    return result.get('text', '')

# Function to transcribe audio in parallel by splitting it into chunks
def transcribe_audio_parallel(wav_data, sr, model, chunk_size_ms=10000):
    # Split audio into chunks
    chunks = split_audio(wav_data, chunk_size_ms, sr)
    
    # Use ThreadPoolExecutor to transcribe chunks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit transcription tasks for each chunk
        futures = [executor.submit(transcribe_chunk, chunk, model, sr) for chunk in chunks]
        
        # Wait for all futures to complete and collect results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Combine all the transcriptions
    full_transcription = ' '.join(results)
    
    return full_transcription

# Sample usage
def transcribe_audio_file(file_path, model, chunk_size_ms=10000):
    # Open the wav file
    with wave.open(file_path, 'rb') as wf:
        # Read the audio data
        wav_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        sr = wf.getframerate()

    # Transcribe the audio in parallel
    transcription = transcribe_audio_parallel(wav_data, sr, model, chunk_size_ms)
    
    return transcription
