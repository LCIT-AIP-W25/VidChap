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

from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials,db
import hashlib


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://vidchap-54042-default-rtdb.firebaseio.com/'
    })


ref = db.reference('/')

def url_to_unique_string(url):
    # Use MD5 for speed (not for cryptographic security)
    return hashlib.md5(url.encode()).hexdigest()

# configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# initialize FastAPI app
app = FastAPI(
    title="YouTube Transcript and Chapter Extractor API",
    description="An API to extract transcripts and chapter segments from YouTube videos.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)


# groq API configuration
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# define request and response models
class YouTubeURLRequest(BaseModel):
    url: str

class TranscriptResponse(BaseModel):
    # full_transcript: str
    chapters: str

# # helper functions
# def download_youtube_audio(url: str) -> str:
#     """download YouTube audio and return the temporary file path."""
#     ydl_opts = {
#         "format": "bestaudio/best",
#         "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),
#         "postprocessors": [{
#             "key": "FFmpegExtractAudio",
#             "preferredcodec": "mp3",
#             "preferredquality": "192",
#         }],
#         "quiet": True,
#         "noprogress": True,
#         "retries": 10,
#         "fragment_retries": 10,
#         "skip_unavailable_fragments": True,
#         "windowsfilenames": True,
#         "nooverwrites": True,
#         "http_chunk_size": 10485760,
#         "continuedl": False,
#         "ignoreerrors": True,
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=True)
#             if not info:
#                 raise ValueError("Failed to retrieve video info")
            
#             temp_path = ydl.prepare_filename(info)
#             temp_path = re.sub(r"\.(webm|m4a)$", ".mp3", temp_path)

#             # Explicit file release
#             if os.path.exists(temp_path):
#                 os.close(os.open(temp_path, os.O_RDWR))  # Force file handle release
#                 os.utime(temp_path, None)
                
#             return temp_path
#     except Exception as e:
#         logger.error(f"Download failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to download YouTube audio: {str(e)}")

def download_youtube_audio(url: str) -> str:
    """Download YouTube audio and return the temporary file path."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tempfile.gettempdir(), "%(id)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": False,  # Change to False to get more detailed logging
        "noprogress": False,  # Change to False to see download progress
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,
        "windowsfilenames": True,
        "nooverwrites": True,
        "http_chunk_size": 10485760,
        "continuedl": False,
        "ignoreerrors": False,  # Change to False to raise errors
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Validate URL first
            try:
                video_info = ydl.extract_info(url, download=False)
                if not video_info:
                    raise ValueError("Could not extract video information")
            except Exception as info_error:
                logger.error(f"Failed to extract video info: {info_error}")
                raise HTTPException(status_code=400, detail=f"Invalid video URL: {info_error}")

            # Download the audio
            info = ydl.extract_info(url, download=True)
            if not info:
                raise ValueError("Failed to retrieve video info or download")
            
            # Construct the output filename
            filename = ydl.prepare_filename(info)
            
            # Convert to MP3 if not already
            mp3_path = re.sub(r"\.(webm|m4a|mkv|mp4)$", ".mp3", filename)
            
            # Explicit file handling
            if os.path.exists(mp3_path):
                logger.info(f"Downloaded audio file: {mp3_path}")
                os.chmod(mp3_path, 0o666)  # Ensure file permissions
                return mp3_path
            else:
                # Try to find the file with a different extension
                possible_extensions = ['.mp3', '.webm', '.m4a', '.mkv', '.mp4']
                for ext in possible_extensions:
                    alt_path = filename.rsplit('.', 1)[0] + ext
                    if os.path.exists(alt_path):
                        logger.info(f"Found audio file with alternative extension: {alt_path}")
                        return alt_path

                raise FileNotFoundError(f"No audio file found after download. Tried: {mp3_path}")

    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        # Print full traceback for more detailed error information
        import traceback
        logger.error(traceback.format_exc())
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
    """
    Get chapter segments from Groq API with aggressive token reduction
    
    Args:
        transcript_text (str): Full transcript text
        formatted_segments (str): Formatted segments with timestamps
    
    Returns:
        str: Consolidated chapter segments without overlaps
    """
    def split_transcript(formatted_segments: str, max_tokens: int = 1500) -> List[str]:
        """
        Split transcript into very small, focused chunks
        
        Args:
            formatted_segments (str): Full formatted segments
            max_tokens (int): Maximum tokens per chunk
        
        Returns:
            List[str]: List of transcript chunks
        """
        def estimate_tokens(text: str) -> int:
            return len(text.split()) * 1.3
        
        # Split into individual segment lines first
        segments = formatted_segments.split('\n')
        
        # Group segments into small chunks
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for segment in segments:
            segment_tokens = estimate_tokens(segment)
            
            if current_tokens + segment_tokens > max_tokens:
                # Current chunk is full, start a new one
                chunks.append('\n'.join(current_chunk))
                current_chunk = [segment]
                current_tokens = segment_tokens
            else:
                current_chunk.append(segment)
                current_tokens += segment_tokens
        
        # Add last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    def get_chunk_chapters(chunk: str, context: str = '') -> str:
        """
        Get chapter segments for a single transcript chunk
        
        Args:
            chunk (str): Transcript chunk
            context (str): Additional context from previous chunks
        
        Returns:
            str: Chapter segments for the chunk
        """
        try:
            prompt = f"""Your task is to PRECISELY identify chapter breaks in this transcript segment.

STRICT GUIDELINES:
- Provide ONLY chapter names and their EXACT timestamp ranges
- MINIMIZE chapter names (max 3-4 words)
- Focus on MAJOR topic transitions
- DO NOT create too many chapters (aim for 3-5 max)

INPUT CONTEXT (use sparingly):
{context}

TRANSCRIPT SEGMENT:
{chunk}

OUTPUT FORMAT (EXACTLY):
[chapter : {{name}} | {{start}} | {{end}}]"""

            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # More deterministic
                max_tokens=512,   # Strict token limit
            )

            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to get chunk chapter segments: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get chunk chapter segments: {str(e)}")

    def consolidate_chapters(chunk_chapters: List[str]) -> str:
        """
        Consolidate chapters from different chunks, removing overlaps
        
        Args:
            chunk_chapters (List[str]): List of chapter segments from different chunks
        
        Returns:
            str: Consolidated, non-overlapping chapter segments
        """
        def parse_timestamp(ts_str: str) -> float:
            """Convert timestamp string to seconds"""
            try:
                h, m, s = map(float, ts_str.replace(',', '.').split(':'))
                return h * 3600 + m * 60 + s
            except Exception:
                return float('inf')

        # Combine and parse chapters
        all_chapters = []
        for chunk_chapter in chunk_chapters:
            chapters = re.findall(r'\[chapter : (.*?) \| (.*?) \| (.*?)\]', chunk_chapter)
            all_chapters.extend(chapters)
        
        # Sort chapters by start time
        all_chapters.sort(key=lambda x: parse_timestamp(x[1]))
        
        # Remove overlapping chapters
        consolidated_chapters = []
        for chapter in all_chapters:
            if not consolidated_chapters or parse_timestamp(chapter[1]) >= parse_timestamp(consolidated_chapters[-1][2]):
                consolidated_chapters.append(chapter)
        
        # Format final output
        final_chapters = [
            f"[chapter : {name} | {start} | {end}]" 
            for name, start, end in consolidated_chapters
        ]
        
        return "\n".join(final_chapters)

    try:
        # Split transcript into very small chunks
        transcript_chunks = split_transcript(formatted_segments)
        
        # Process chunks with context
        chunk_chapters = []
        previous_context = ''
        for chunk in transcript_chunks:
            chunk_chapter = get_chunk_chapters(chunk, previous_context)
            chunk_chapters.append(chunk_chapter)
            previous_context += chunk_chapter  # Build context for next iteration
        
        # Consolidate chapters
        final_chapters = consolidate_chapters(chunk_chapters)
        
        return final_chapters
    
    except Exception as e:
        logger.error(f"Failed to process chapters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chapters: {str(e)}")

    def get_chunk_chapters(chunk: str) -> str:
        """
        Get chapter segments for a single transcript chunk
        
        Args:
            chunk (str): Transcript chunk
        
        Returns:
            str: Chapter segments for the chunk
        """
        try:
            prompt = f"""Analyze this transcript segment and identify natural chapter breaks. 
    For each chapter provide:
    1. Chapter name
    2. Starting timestamp
    3. Ending timestamp

    Use format:
    [chapter : {{name}} | {{start}} | {{end}}]
    Just give me chapter info in the given format nothing else
    Transcript Segment:
    {chunk}"""

            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )

            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to get chunk chapter segments: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get chunk chapter segments: {str(e)}")

    def consolidate_chapters(chunk_chapters: List[str]) -> str:
        """
        Consolidate chapters from different chunks, removing overlaps
        
        Args:
            chunk_chapters (List[str]): List of chapter segments from different chunks
        
        Returns:
            str: Consolidated, non-overlapping chapter segments
        """
        # Combine and parse chapters
        all_chapters = []
        for chunk_chapter in chunk_chapters:
            # Basic parsing of chapter segments
            chapters = re.findall(r'\[chapter : (.*?) \| (.*?) \| (.*?)\]', chunk_chapter)
            all_chapters.extend(chapters)
        
        # Sort chapters by start time
        all_chapters.sort(key=lambda x: x[1])
        
        # Remove overlapping chapters
        consolidated_chapters = []
        for chapter in all_chapters:
            if not consolidated_chapters or chapter[1] > consolidated_chapters[-1][2]:
                consolidated_chapters.append(chapter)
        
        # Format final output
        final_chapters = [
            f"[chapter : {name} | {start} | {end}]" 
            for name, start, end in consolidated_chapters
        ]
        
        return "\n".join(final_chapters)

    try:
        # Split transcript into chunks
        transcript_chunks = split_transcript(formatted_segments)
        
        # Process each chunk
        chunk_chapters = []
        for chunk in transcript_chunks:
            chunk_chapters.append(get_chunk_chapters(chunk))
        
        # Consolidate chapters
        final_chapters = consolidate_chapters(chunk_chapters)
        
        return final_chapters
    
    except Exception as e:
        logger.error(f"Failed to process chapters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chapters: {str(e)}")
    

    
def transcribe_with_timestamps(
    audio_path: str,
    model_size: str = "small",
    language: str = "en",
    compute_type: str = "int8",
    num_processes: int = 5,
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
    requrl = url_to_unique_string(request.url)

    if ref.child(requrl).get() is not None:
        chapters = ref.child(requrl).get()
    
        logger.info(f"Retrieved from database cache")
        return  TranscriptResponse( chapters=chapters)
    else:
        """process a YouTube video and return the transcript and chapters."""
        try:
            full_transcript, chapters = process_youtube_video(request.url)
            ref.child(requrl).set(chapters)
            
            logger.info(f"Added to database cache")
            return TranscriptResponse( chapters=chapters)
    
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




#todo
# run command on render after req installation
# uvicorn m3:app --host 0.0.0.0 --port 10000

# crucial dependencies 
#  yt-dlp pydub fastapi faster-whisper