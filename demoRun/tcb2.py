import yt_dlp
import re
import logging
from backend_python import (
    convert_mp3_to_wav,
    load_vosk_model,
    transcribe_audio,
    format_transcriptions
)
from groq import Groq

VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"  
GROQ_API_KEY = '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'
client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def extract_video_id(url):
    patterns = [
        r"^https?://(?:www\.)?youtube\.com/watch\?v=([^&]+)",
        r"^https?://youtu\.be/([^?]+)",
        r"^https?://(?:www\.)?youtube\.com/embed/([^/?]+)"
    ]
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None


def process_video_transcript(video_url):
    
    video_id = extract_video_id(video_url)
    
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {video_url}")
    
    ydl_opts = {
        "format": "bestaudio/best",
        #"outtmpl": "./%(title)s.%(ext)s",
        "outtmpl": f"./{video_id}.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        mp3_path = info['requested_downloads'][0]['filepath']
        print("donwload?")
    wav_data, sr = convert_mp3_to_wav(mp3_path)
    model = load_vosk_model(VOSK_MODEL_PATH)

    transcripts = transcribe_audio(wav_data, sr, model)
    formatted = format_transcriptions(transcripts)

    # with open("data.txt", "w") as file:
    #     logging.debug("In Progress writing the file on disk")
    #     file.write(formatted)

    logging.debug("Done")

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"Give me chapter names and timestamps of appropriate lengths based on the given transcript,  Note that the timestamps should be based on discussed topic and not the 10 seconds chunks in the given transcript, return in this specified format start of data [chapter : chapter name start time end time] end of data:\n\n{formatted}"
        }],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    result = ""
    for chunk in completion:
        result += chunk.choices[0].delta.content or ""

    return result


if __name__ == "__main__":
    video_url = "https://youtu.be/jmmW0F0biz0?si=BAA5cBaz1IGV2quI"
    transcript = process_video_transcript(video_url)
    print(transcript)
