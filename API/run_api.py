import os
import tempfile
import re
import logging
import multiprocessing as mp
from typing import List, Dict, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from faster_whisper import WhisperModel
from pydub import AudioSegment
import numpy as np
import yt_dlp
from groq import Groq

# configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# initialize FastAPI app
app = FastAPI(
    title="YouTube Transcript and Chapter Extractor API",
    description="An API to extract transcripts and chapter segments from YouTube videos.",
    version="1.0.0",
)

# groq API configuration
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# define request and response models
class YouTubeURLRequest(BaseModel):
    url: str

class TranscriptResponse(BaseModel):
    full_transcript: str
    chapters: str

# helper functions
def download_youtube_audio(url: str) -> str:
    """download YouTube audio and return the temporary file path."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "noprogress": True,
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,
        "windowsfilenames": True,
        "nooverwrites": True,
        "http_chunk_size": 10485760,
        "continuedl": False,
        "ignoreerrors": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise ValueError("Failed to retrieve video info")
            
            temp_path = ydl.prepare_filename(info)
            temp_path = re.sub(r"\.(webm|m4a)$", ".mp3", temp_path)

            # Explicit file release
            if os.path.exists(temp_path):
                os.close(os.open(temp_path, os.O_RDWR))  # Force file handle release
                os.utime(temp_path, None)
                
            return temp_path
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download YouTube audio: {str(e)}")

def split_audio(audio_path: str, chunk_length_ms: int) -> List[Dict]:
    """split audio into chunks for parallel processing."""
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        duration_ms = len(audio)
        
        chunks = []
        for start_ms in range(0, duration_ms, chunk_length_ms):
            end_ms = start_ms + chunk_length_ms
            chunk = audio[start_ms:end_ms]
            
            samples = chunk.get_array_of_samples()
            np_array = np.array(samples, dtype=np.float32) / 32768.0
            
            chunks.append({
                "audio_array": np_array,
                "sample_rate": 16000,
                "start_time": start_ms / 1000.0,
                "end_time": min(end_ms / 1000.0, duration_ms / 1000.0),
            })
        
        return chunks
    except Exception as e:
        logger.error(f"Failed to split audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to split audio: {str(e)}")

def init_worker(model_size: str, compute_type: str):
    """initialize worker process with Whisper model."""
    global worker_model
    worker_model = WhisperModel(
        model_size,
        device="cpu",
        compute_type=compute_type,
    )

def transcribe_chunk(chunk: Dict, language: str) -> Tuple[str, List[Dict]]:
    """transcribe a single audio chunk."""
    try:
        audio_array = chunk["audio_array"]
        start_time = chunk["start_time"]
        
        segments, _ = worker_model.transcribe(
            audio_array,
            language=language,
            beam_size=5,
            word_timestamps=True,
        )
        
        transcript_segments = []
        full_transcript = []
        for segment in segments:
            adjusted_start = segment.start + start_time
            adjusted_end = segment.end + start_time
            
            transcript_segments.append({
                "start": adjusted_start,
                "end": adjusted_end,
                "text": segment.text.strip(),
                "start_time": format_timestamp(adjusted_start),
                "end_time": format_timestamp(adjusted_end),
            })
            full_transcript.append(segment.text.strip())
        
        return " ".join(full_transcript), transcript_segments
    except Exception as e:
        logger.error(f"Failed to transcribe chunk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to transcribe chunk: {str(e)}")

def format_timestamp(seconds: float) -> str:
    """convert seconds to SRT timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:06.3f}".replace(".", ",")

def format_for_llm(segments: List[Dict]) -> str:
    """format segments with timestamps for LLM input."""
    return "\n".join(
        [f"[{seg['start_time']} --> {seg['end_time']}] {seg['text']}" 
         for seg in segments]
    )

def get_chapter_segments(transcript_text: str, formatted_segments: str) -> str:
    """get chapter segments from Groq API."""
    try:
        prompt = f"""Analyze this transcript and identify natural chapter breaks. 
For each chapter provide:
1. Chapter name
2. Starting timestamp
3. Ending timestamp

Use format:
[chapter : {{name}} | {{start}} | {{end}}]
Just give me chapter info in the given format nothing else
Transcript:
{formatted_segments}"""

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
        )

        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Failed to get chapter segments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chapter segments: {str(e)}")

def transcribe_with_timestamps(
    audio_path: str,
    model_size: str = "small",
    language: str = "en",
    compute_type: str = "int8",
    num_processes: int = 4,
    chunk_length: int = 30
) -> Tuple[str, List[Dict]]:
    """transcribe audio with timestamps using multiprocessing."""
    try:
        chunks = split_audio(audio_path, chunk_length * 1000)
        
        # Use spawn context for multiprocessing
        ctx = mp.get_context('spawn')
        with ctx.Pool(
            processes=num_processes,
            initializer=init_worker,
            initargs=(model_size, compute_type)
        ) as pool:
            args_list = [(chunk, language) for chunk in chunks]
            results = pool.starmap(transcribe_chunk, args_list)
        
        # Combine results
        full_transcript_parts = []
        all_segments = []
        for full_part, segments in results:
            full_transcript_parts.append(full_part)
            all_segments.extend(segments)
        
        all_segments.sort(key=lambda x: x['start'])
        return " ".join(full_transcript_parts), all_segments
    except Exception as e:
        logger.error(f"Failed to transcribe audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {str(e)}")

def process_youtube_video(url: str) -> Tuple[str, str]:
    """main processing pipeline for YouTube URLs."""
    temp_audio_path = None
    try:
        temp_audio_path = download_youtube_audio(url)
        full_text, segments = transcribe_with_timestamps(temp_audio_path)
        formatted_segments = format_for_llm(segments)
        chapters = get_chapter_segments(full_text, formatted_segments)
        return full_text, chapters
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

# API Endpoint
@app.post("/process-youtube", response_model=TranscriptResponse)
async def process_youtube(request: YouTubeURLRequest):
    """process a YouTube video and return the transcript and chapters."""
    try:
        full_transcript, chapters = process_youtube_video(request.url)
        return TranscriptResponse(full_transcript=full_transcript, chapters=chapters)
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




#todo
# get the chapter details from regex or include it in the current code above and return just the chapter data 
# run command on render after req installation
# uvicorn m3:app --host 0.0.0.0 --port 10000
