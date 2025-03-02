from faster_whisper import WhisperModel
from typing import List, Dict, Tuple
from pydub import AudioSegment
import numpy as np
import multiprocessing as mp
from groq import Groq
import os

# API Key Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your_default_api_key_here')
client = Groq(api_key=GROQ_API_KEY)

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

def generate_chapter_segments(transcript: str, segments: List[Dict]) -> str:
    """Generates chapter breaks based on the transcript using Groq's API."""
    formatted_segments = "\n".join(f"[{seg['formatted_start']} -> {seg['formatted_end']}] {seg['text']}" for seg in segments)
    prompt = f"""
        Identify natural chapter breaks from the following transcript based on topic shifts.
        Format:
        [chapter: {{name}} | {{start_timestamp}} | {{end_timestamp}}]
        
        Transcript:
        {formatted_segments}
    """
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=False,
    )
    
    return response.choices[0].message.content

def process_audio(audio_path: str) -> Tuple[str, str]:
    """Processes the audio file, transcribes it, and generates chapter segmentation."""
    transcript, segments = transcribe_audio(audio_path)
    chapter_segments = generate_chapter_segments(transcript, segments)
    return transcript, chapter_segments

if __name__ == "__main__":
    input_file = "i3.mp3"
    full_transcript, chapter_result = process_audio(input_file)
    
    print("\nFull Transcript:")
    print(full_transcript)
    
    print("\nChapter Segmentation:")
    print(chapter_result)



#------------------------- New Features to be added ----------------# 

#Batched Transcription

# from faster_whisper import WhisperModel, BatchedInferencePipeline

# model = WhisperModel("turbo", device="cuda", compute_type="float16")
# batched_model = BatchedInferencePipeline(model=model)
# segments, info = batched_model.transcribe("audio.mp3", batch_size=16)

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))


#Faster Distil-Whisper

# from faster_whisper import WhisperModel

# model_size = "distil-large-v3"

# model = WhisperModel(model_size, device="cuda", compute_type="float16")
# segments, info = model.transcribe("audio.mp3", beam_size=5, language="en", condition_on_previous_text=False)

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

#Word-level timestamps

# segments, _ = model.transcribe("audio.mp3", word_timestamps=True)

# for segment in segments:
#     for word in segment.words:
#         print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
