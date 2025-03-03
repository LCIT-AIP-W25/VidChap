import cv2
import json
import os
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

def detect_scenes(video_path, threshold=30.0):
    """
    Detect scene changes in a video using PySceneDetect.
    Returns a list of timestamps where scene changes occur.
    """
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    
    # Use ContentDetector (histogram-based scene change detection)
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    
    scene_list = scene_manager.get_scene_list()
    
    # Convert scene timestamps to seconds
    scene_timestamps = [(start.get_seconds(), end.get_seconds()) for start, end in scene_list]

    return scene_timestamps

def save_chapters(video_name, chapter_timestamps, output_file="chapters.json"):
    """
    Save chapter timestamps to a JSON file.
    """
    chapter_data = {
        "video": video_name,
        "chapters": [{"start": start, "end": end} for start, end in chapter_timestamps]
    }
    
    # Save to a JSON file
    with open(output_file, "w") as json_file:
        json.dump(chapter_data, json_file, indent=4)
    
    print(f"Chapters saved to {output_file}")

def process_video(video_path):
    """
    Processes the video and extracts scene-based chapter timestamps.
    """
    print(f"Processing video: {video_path}")
    chapters = detect_scenes(video_path)
    save_chapters(os.path.basename(video_path), chapters)

if __name__ == "__main__":
    video_file = "example_video.mp4"  
    process_video(video_file)
