from faster_whisper import WhisperModel
from typing import List, Dict, Tuple
from pydub import AudioSegment
import numpy as np
import multiprocessing as mp
import os

def transcribe_audio(
    audio_path: str,
    model_size: str = "medium",
    language: str = "en",
    compute_type: str = "int8",
    num_workers: int = 4,
    chunk_duration: int = 30
) -> Tuple[str, List[Dict]]:
    """
    Transcribes an audio file using FasterWhisper with multiprocessing.
    
    Args:
        audio_path (str): Path to the audio file.
        model_size (str): Whisper model size to use.
        language (str): Language for transcription.
        compute_type (str): Computation precision.
        num_workers (int): Number of parallel processes.
        chunk_duration (int): Duration (in seconds) for splitting audio.

    Returns:
        Tuple[str, List[Dict]]: Full transcript and list of segments with timestamps.
    """
    audio_chunks = split_audio(audio_path, chunk_duration * 1000)
    
    with mp.Pool(processes=num_workers, initializer=init_worker, initargs=(model_size, compute_type)) as pool:
        results = pool.starmap(transcribe_chunk, [(chunk, language) for chunk in audio_chunks])
    
    return merge_transcriptions(results)

def split_audio(audio_path: str, chunk_length_ms: int) -> List[Dict]:
    """Splits audio into smaller segments for efficient processing."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Error: Audio file not found -> {audio_path}")

    audio = AudioSegment.from_file(audio_path).set_channels(1).set_frame_rate(16000)
    duration_ms = len(audio)
    
    return [
        {
            'audio_array': np.array(audio[start:start + chunk_length_ms].get_array_of_samples(), dtype=np.float32) / 32768.0,
            'sample_rate': 16000,
            'start_time': start / 1000.0,
            'end_time': min((start + chunk_length_ms) / 1000.0, duration_ms / 1000.0)
        }
        for start in range(0, duration_ms, chunk_length_ms)
    ]

def init_worker(model_size: str, compute_type: str):
    """Initializes the WhisperModel for worker processes."""
    global whisper_model
    whisper_model = WhisperModel(model_size, device="cpu", compute_type=compute_type)

def transcribe_chunk(chunk: Dict, language: str) -> Tuple[str, List[Dict]]:
    """Processes a single audio chunk and extracts text with timestamps."""
    segments, _ = whisper_model.transcribe(chunk['audio_array'], language=language, beam_size=5, word_timestamps=True)
    
    return " ".join(seg.text.strip() for seg in segments), [
        {
            'start': seg.start + chunk['start_time'],
            'end': seg.end + chunk['start_time'],
            'text': seg.text.strip(),
            'formatted_start': format_timestamp(seg.start + chunk['start_time']),
            'formatted_end': format_timestamp(seg.end + chunk['start_time'])
        }
        for seg in segments
    ]

def merge_transcriptions(results: List[Tuple[str, List[Dict]]]) -> Tuple[str, List[Dict]]:
    """Combines transcriptions from all chunks into a single output."""
    transcript = " ".join(text for text, _ in results)
    segments = sorted([seg for _, seg_list in results for seg in seg_list], key=lambda x: x['start'])
    return transcript, segments

def format_timestamp(seconds: float) -> str:
    """Formats timestamps into HH:MM:SS,mmm format."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}".replace('.', ',')

def process_audio(audio_path: str) -> str:
    """Transcribes an audio file and returns the full transcript."""
    transcript, _ = transcribe_audio(audio_path)
    return transcript

if __name__ == "__main__":
    input_file = "audio.mp3"
    
    # Convert relative path to absolute path
    abs_path = os.path.abspath(input_file)

    if not os.path.exists(abs_path):
        print(f"Error: File not found -> {abs_path}")
    else:
        print(f"Processing file: {abs_path}")
        full_transcript = process_audio(abs_path)
        print("\nFull Transcript:")
        print(full_transcript)

# Faster Distil-Whisper

def distil_whisper_transcription(audio_path: str, model_size: str = "distil-large-v3"):
    """Uses a distilled model for faster transcription."""
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    segments, _ = model.transcribe(audio_path, beam_size=5, language="en", condition_on_previous_text=False)
    
    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

# Word-Level Timestamps

def word_level_timestamps(audio_path: str, model_size: str = "medium"):
    """Extracts timestamps for each word spoken in the audio."""
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    segments, _ = model.transcribe(audio_path, word_timestamps=True)
    
    for segment in segments:
        for word in segment.words:
            print(f"[{word.start:.2f}s -> {word.end:.2f}s] {word.word}")
