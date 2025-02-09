import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://devuser:securepassword@localhost:27017/mydatabase")
    TRANSCRIPTION_MODEL_PATH = os.getenv("MODEL_PATH", "models/vosk-model")
    CHUNK_SIZE_MS = int(os.getenv("CHUNK_SIZE_MS", "10000"))
