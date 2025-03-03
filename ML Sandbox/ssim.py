import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim

'''
 Extracts frames at regular intervals
 Compares consecutive frames using SSIM
 Marks timestamps where significant scene changes occur
 Outputs a list of chapter timestamps'''

def extract_frames(video_path, interval=30, frames_per_interval=15):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_timestamps = []
    frames = []

    for sec in range(0, int(total_frames / fps), interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, sec * fps)
        for i in range(frames_per_interval):
            success, frame = cap.read()
            if success:
                frames.append(frame)
                frame_timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            else:
                break

    cap.release()
    return frames, frame_timestamps

def detect_scene_changes(frames, timestamps, threshold=0.5):
    chapter_timestamps = [timestamps[0]]
    
    for i in range(1, len(frames)):
        gray1 = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)

        # Structural Similarity Index (SSIM) for scene change detection
        score, _ = ssim(gray1, gray2, full=True)
        
        if score < threshold:
            chapter_timestamps.append(timestamps[i])

    return chapter_timestamps

def process_video(video_path):
    frames, timestamps = extract_frames(video_path)
    chapter_timestamps = detect_scene_changes(frames, timestamps)
    
    return chapter_timestamps

if __name__ == "__main__":
    video_file = "example_video.mp4"  
    chapters = process_video(video_file)
    print("Chapter Boundaries:", chapters)
