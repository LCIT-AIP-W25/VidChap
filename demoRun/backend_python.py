import subprocess
import json
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import io
import logging

logger = logging.getLogger(__name__)

def convert_mp3_to_wav(mp3_file: str) -> tuple[bytes, int]:

    logger.info(f"Converting MP3 file '{mp3_file}' to WAV format...")
    command = [
        "ffmpeg", "-i", mp3_file, "-ac", "1", "-ar", "16000",
        "-sample_fmt", "s16", "-f", "wav", "pipe:1"
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        error_msg = f"FFmpeg conversion failed: {result.stderr.decode()}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    return result.stdout, 16000

def load_vosk_model(model_path: str) -> Model:
    logger.info(f"Loading Vosk model from '{model_path}'...")
    try:
        return Model(model_path)
    except Exception as e:
        logger.error(f"Failed to load Vosk model: {str(e)}")
        raise

def transcribe_audio_not_working(
    audio_data: bytes,
    sample_rate: int,
    model: Model,
    chunk_duration_ms: int = 10000
) -> list[str]:

    def _chunk_to_wav_bytes(chunk: AudioSegment) -> bytes:
        """Convert AudioSegment chunk to WAV bytes."""
        with io.BytesIO() as buffer:
            chunk.export(buffer, format="wav")
            return buffer.getvalue()

    logger.info(f"Starting transcription with {chunk_duration_ms}ms chunks...")
    
    recognizer = KaldiRecognizer(model, sample_rate)
    audio = AudioSegment.from_wav(io.BytesIO(audio_data))
    transcriptions = []

    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        wav_bytes = _chunk_to_wav_bytes(chunk)
        
        if recognizer.AcceptWaveform(wav_bytes):
            result = json.loads(recognizer.Result())
            text = result.get('text', '')
            timestamp = i / 1000  # Convert to seconds
        
        entry = (
            f"Timestamp: {timestamp:.2f}s - Text: {text}" if text 
            else f"Timestamp: {timestamp:.2f}s - Text: [silence]"
        )
        transcriptions.append(entry)
        logger.debug(entry)

    # Process final result
    final_result = json.loads(recognizer.FinalResult())
    if final_text := final_result.get('text', ''):
        timestamp = len(audio) / 1000
        final_entry = f"Timestamp: {timestamp:.2f}s - Text: {final_text}"
        transcriptions.append(final_entry)
        logger.debug(final_entry)

    logger.info(f"Completed transcription of {len(audio)/1000:.2f}s audio")
    return transcriptions

def transcribe_audio_working(
    audio_data: bytes,
    sample_rate: int,
    model: Model,
    chunk_duration_ms: int = 10000
) -> list[str]:
    def _chunk_to_wav_bytes(chunk: AudioSegment) -> bytes:
        with io.BytesIO() as buffer:
            chunk.export(buffer, format="wav")
            return buffer.getvalue()

    logger.info(f"Starting transcription with {chunk_duration_ms}ms chunks...")
    
    recognizer = KaldiRecognizer(model, sample_rate)
    audio = AudioSegment.from_wav(io.BytesIO(audio_data))
    transcriptions = []

    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        wav_bytes = _chunk_to_wav_bytes(chunk)
        text = ""
        timestamp = i / 1000  

        if recognizer.AcceptWaveform(wav_bytes):
            result = json.loads(recognizer.Result())
            text = result.get('text', '').strip()

        entry = (f"Timestamp: {timestamp:.2f}s - Text: {text}" if text 
                else f"Timestamp: {timestamp:.2f}s - Text: [silence]")
        transcriptions.append(entry)
        logger.debug(entry)

    final_result = json.loads(recognizer.FinalResult())
    if final_text := final_result.get('text', ''):
        timestamp = len(audio) / 1000
        final_entry = f"Timestamp: {timestamp:.2f}s - Text: {final_text}"
        transcriptions.append(final_entry)
        logger.debug(final_entry)

    logger.info(f"Completed transcription of {len(audio)/1000:.2f}s audio")
    return transcriptions

def format_transcriptions(transcriptions: list[str]) -> str:
    return " ".join(transcriptions)



def transcribe_audio(
    audio_data: bytes,
    sample_rate: int,
    model: Model,
    chunk_duration_ms: int = 10000,
    progress_callback: callable = None  
) -> list[str]:
    def _chunk_to_wav_bytes(chunk: AudioSegment) -> bytes:
        with io.BytesIO() as buffer:
            chunk.export(buffer, format="wav")
            return buffer.getvalue()

    logger.info(f"Starting transcription with {chunk_duration_ms}ms chunks...")
    
    recognizer = KaldiRecognizer(model, sample_rate)
    audio = AudioSegment.from_wav(io.BytesIO(audio_data))
    transcriptions = []
    
    total_chunks = len(audio) // chunk_duration_ms + (1 if len(audio) % chunk_duration_ms != 0 else 0)
    current_chunk = 0

    for i in range(0, len(audio), chunk_duration_ms):
        current_chunk += 1
        chunk = audio[i:i + chunk_duration_ms]
        wav_bytes = _chunk_to_wav_bytes(chunk)
        text = ""
        timestamp = i / 1000

        if recognizer.AcceptWaveform(wav_bytes):
            result = json.loads(recognizer.Result())
            text = result.get('text', '').strip()

        entry = (f"Timestamp: {timestamp:.2f}s - Text: {text}" if text 
                else f"Timestamp: {timestamp:.2f}s - Text: [silence]")
        transcriptions.append(entry)
        logger.debug(entry)
        
        if progress_callback and total_chunks > 0:
            progress = int((current_chunk / total_chunks) * 100)
            progress_callback(progress)

    final_result = json.loads(recognizer.FinalResult())
    if final_text := final_result.get('text', ''):
        timestamp = len(audio) / 1000
        final_entry = f"Timestamp: {timestamp:.2f}s - Text: {final_text}"
        transcriptions.append(final_entry)
        logger.debug(final_entry)

    logger.info(f"Completed transcription of {len(audio)/1000:.2f}s audio")
    return transcriptions

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        wav_data, sample_rate = convert_mp3_to_wav("audio.mp3")
        
        model = load_vosk_model("vosk-model-small-en-us-0.15")
        
        transcriptions = transcribe_audio(wav_data, sample_rate, model)
        
        formatted = format_transcriptions(transcriptions)
        print("\nFinal Transcript:")
        print(formatted)
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise
