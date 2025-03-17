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
    Transcribes audio using parallel processing with FasterWhisper.
    Returns:
        - Full transcript as a string
        - List of segment dictionaries with timestamps
    """
    audio_chunks = split_audio(audio_path, chunk_duration * 1000)
    
    with mp.Pool(processes=num_workers, initializer=init_worker, initargs=(model_size, compute_type)) as pool:
        results = pool.starmap(transcribe_chunk, [(chunk, language) for chunk in audio_chunks])
    
    transcript, segments = merge_transcriptions(results)
    return transcript, segments

def split_audio(audio_path: str, chunk_length_ms: int) -> List[Dict]:
    """Splits audio into smaller chunks for efficient processing."""
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
    """Initializes WhisperModel for worker processes."""
    global whisper_model
    whisper_model = WhisperModel(model_size, device="cpu", compute_type=compute_type)

def transcribe_chunk(chunk: Dict, language: str) -> Tuple[str, List[Dict]]:
    """Transcribes a single chunk of audio and returns formatted output."""
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
    """Merges transcript and segments from multiple chunks."""
    transcript = " ".join(text for text, _ in results)
    segments = sorted([seg for _, seg_list in results for seg in seg_list], key=lambda x: x['start'])
    return transcript, segments

def format_timestamp(seconds: float) -> str:
    """Formats timestamps in HH:MM:SS,mmm format for subtitles."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}".replace('.', ',')

def process_audio(audio_path: str) -> str:
    """Processes the audio file and transcribes it."""
    transcript, _ = transcribe_audio(audio_path)
    return transcript

if __name__ == "__main__":
    input_file = "audio.mp3"
    full_transcript = process_audio(input_file)
    
    print("\nFull Transcript:")
    print(full_transcript)

# Batched Transcription
from faster_whisper import WhisperModel, BatchedInferencePipeline

def batched_transcription(audio_path: str, model_size: str = "turbo", batch_size: int = 16):
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    batched_model = BatchedInferencePipeline(model=model)
    segments, _ = batched_model.transcribe(audio_path, batch_size=batch_size)
    
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

# Faster Distil-Whisper

def distil_whisper_transcription(audio_path: str, model_size: str = "distil-large-v3"):
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    segments, _ = model.transcribe(audio_path, beam_size=5, language="en", condition_on_previous_text=False)
    
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

# Word-Level Timestamps

def word_level_timestamps(audio_path: str, model_size: str = "medium"):
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    segments, _ = model.transcribe(audio_path, word_timestamps=True)
    
    for segment in segments:
        for word in segment.words:
            print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
