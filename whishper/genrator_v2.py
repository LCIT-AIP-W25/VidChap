from faster_whisper import WhisperModel
from typing import List, Dict, Tuple
from pydub import AudioSegment
import numpy as np
import multiprocessing as mp
from groq import Groq
import os 


# VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"  
GROQ_API_KEY = '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'
client = Groq(api_key=GROQ_API_KEY)


def transcribe_with_timestamps(
    audio_path: str,
    model_size: str = "small",
    language: str = "en",
    compute_type: str = "int8",
    num_processes: int = 4,
    chunk_length: int = 30 # Chunk size in seconds
) -> Tuple[str, List[Dict]]:
    """
    Transcribe audio with parallel processing using FasterWhisper
    
    Returns:
        Tuple containing:
        - Full transcript text
        - List of segments with timestamps
    """
    # Split audio into chunks
    chunks = split_audio(audio_path, chunk_length * 1000)
    
    # Create multiprocessing pool
    with mp.Pool(
        processes=num_processes,
        initializer=init_worker,
        initargs=(model_size, compute_type)
    ) as pool:
        args_list = [(chunk, language) for chunk in chunks]
        results = pool.starmap(transcribe_chunk, args_list)
    
    # Combine results from all chunks
    full_transcript_parts = []
    all_segments = []
    for full_part, segments in results:
        full_transcript_parts.append(full_part)
        all_segments.extend(segments)
    
    # Sort segments by start time to maintain original order
    all_segments.sort(key=lambda x: x['start'])
    
    return " ".join(full_transcript_parts), all_segments

def split_audio(audio_path: str, chunk_length_ms: int) -> List[Dict]:
    """Split audio into chunks for parallel processing"""
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # Convert to mono, 16kHz
    duration_ms = len(audio)
    
    chunks = []
    for start_ms in range(0, duration_ms, chunk_length_ms):
        end_ms = start_ms + chunk_length_ms
        chunk = audio[start_ms:end_ms]
        
        # Convert to numpy array for Whisper
        samples = chunk.get_array_of_samples()
        np_array = np.array(samples, dtype=np.float32) / 32768.0  # Convert to float32
        
        chunks.append({
            'audio_array': np_array,
            'sample_rate': 16000,
            'start_time': start_ms / 1000.0,
            'end_time': min(end_ms / 1000.0, duration_ms / 1000.0)
        })
    
    return chunks

def init_worker(model_size: str, compute_type: str):
    """Initialize worker process with Whisper model"""
    global worker_model
    worker_model = WhisperModel(
        model_size,
        device="cpu",
        compute_type=compute_type
    )

def transcribe_chunk(chunk: Dict, language: str) -> Tuple[str, List[Dict]]:
    """Transcribe a single audio chunk"""
    audio_array = chunk['audio_array']
    start_time = chunk['start_time']
    
    # Transcribe using the pre-initialized model
    segments, _ = worker_model.transcribe(
        audio_array,
        language=language,
        beam_size=5,
        word_timestamps=True
    )
    
    transcript_segments = []
    full_transcript = []
    for segment in segments:
        # Adjust timestamps to original audio timeline
        adjusted_start = segment.start + start_time
        adjusted_end = segment.end + start_time
        
        transcript_segments.append({
            'start': adjusted_start,
            'end': adjusted_end,
            'text': segment.text.strip(),
            'start_time': format_timestamp(adjusted_start),
            'end_time': format_timestamp(adjusted_end)
        })
        full_transcript.append(segment.text.strip())
    
    return " ".join(full_transcript), transcript_segments

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:06.3f}".replace('.', ',')

def format_for_llm(segments: List[Dict]) -> str:
    """Format segments with timestamps for LLM input"""
    return "\n".join(
        [f"[{seg['start_time']} --> {seg['end_time']}] {seg['text']}" 
         for seg in segments]
    )

def get_chapter_segments(transcript_text: str, formatted_segments: str) -> str:
    """Get chapter segments from Groq API"""
    prompt = f"""Analyze this transcript and identify natural chapter breaks based on topic changes. 
For each chapter, provide:
1. Meaningful chapter name reflecting the topic
2. Starting timestamp of when the topic begins
3. Ending timestamp of when the topic concludes

Use this exact format for each chapter:
[chapter : {{chapter_name}} | {{start_timestamp}} | {{end_timestamp}}]

Transcript with timestamps:
{formatted_segments}"""

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=False,
    )

    return completion.choices[0].message.content

def process_audio(audio_path: str) -> Tuple[str, str]:
    """Main processing pipeline"""
    # Get transcription
    full_text, segments = transcribe_with_timestamps(audio_path)
    
    # Format segments for LLM
    formatted_segments = format_for_llm(segments)
    
    # Get chapter segmentation from LLM
    chapters = get_chapter_segments(full_text, formatted_segments)
    
    return full_text, chapters

if __name__ == "__main__":
    
    input_file = "i3.mp3"
    full_transcript, chapter_result = process_audio(input_file)
    
    print("\nFull Transcript:")
    print(full_transcript)
    
    print("\nChapter Segmentation:")
    print(chapter_result)