from tcb2 import process_video_transcript
import json
from pytube import YouTube
import os
from yt_dlp import YoutubeDL


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def is_video_available(video_url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "ignoreerrors": True
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(video_url, download=False)
            return result is not None  
    except Exception as e:
        print(f"Skipping {video_url}: {e}")

def process_dataset(json_path, output_path, sample_size=None):
    data = load_json(json_path)

    video_ids = [vid for vid, details in data.items() if details["duration"] < 300]
    
    if sample_size:
        video_ids = video_ids[:sample_size]

    generated_texts = {}  

    for v in video_ids:
        url = f"https://www.youtube.com/watch?v={v}"

        if is_video_available(url):
            print(f"Processing: {url}")
            generated_text = process_video_transcript(url)
            generated_texts[v] = generated_text
        else:
            print(f"Skipping unavailable video: {url}")

    save_json(generated_texts, output_path)


process_dataset("chapters_dvc_test.json", "output.json", sample_size=30)







#------------------
# from tcb2 import process_video_transcript
# import json 
# import os 

# import json

# # def load_json(file_path):
# #     with open(file_path, 'r', encoding='utf-8') as file:
# #         return json.load(file)

# # def process_dataset(json_path, sample_size=None):
# #     data = load_json(json_path)
    
# #     # Filter video IDs where duration is less than 300 seconds (5 minutes)
# #     video_ids = [vid for vid, details in data.items() if details["duration"] < 300]
    
# #     # Limit to the sample size if provided
# #     if sample_size:
# #         video_ids = video_ids[:sample_size]

# #     for v in video_ids:
# #         url = f"https://www.youtube.com/watch?v={v}"
# #         print(url)


# # process_dataset("chapters_dvc_test.json", sample_size=10)



# def load_json(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return json.load(file)

# def save_json(data, file_path):
#     with open(file_path, 'w', encoding='utf-8') as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)

# def process_dataset(json_path, output_path, sample_size=None):
#     data = load_json(json_path)
    
#     video_ids = [vid for vid, details in data.items() if details["duration"] < 300]
    
#     if sample_size:
#         video_ids = video_ids[:sample_size]

#     generated_texts = {}  # Store generated text data

#     for v in video_ids:
#         url = f"https://www.youtube.com/watch?v={v}"
#         print(url)

#         generated_text = process_video_transcript(url)

#         # Store the text with YouTube ID as the key
#         generated_texts[v] = generated_text

#     save_json(generated_texts, output_path)

# process_dataset("chapters_dvc_test.json", "output.json", sample_size=30)
# # process_dataset("chapters_dvc_test.json", sample_size=10)



# # video_url = "https://youtu.be/jmmW0F0biz0?si=BAA5cBaz1IGV2quI"
# # transcript = process_video_transcript(video_url)
# # print(transcript)
