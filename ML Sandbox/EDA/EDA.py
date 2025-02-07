import ijson
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_youtube_data_sample(json_file, max_records=100):
    """
    Efficiently processes a large JSON file containing YouTube video data to check if the code works.

    Args:
        json_file (str): Path to the JSON file.
        max_records (int): Maximum number of records to process.

    Returns:
        pd.DataFrame: A DataFrame containing video validation results.
    """
    base_url = "https://www.youtube.com/watch?v="
    results = []
    
    with open(json_file, 'r') as file:
        parser = ijson.items(file, "item")  # Optimized parsing
        
        for i, item in enumerate(parser):
            if not isinstance(item, dict):
                continue  # Skip invalid entries
            
            video_id = item.get("video_id", "Unknown")
            results.append({
                "Video ID": video_id,
                "URL": f"{base_url}{video_id}",
                "Valid": None,  # Placeholder
                "Duration": item.get("duration", 0),
                "Sentences": item.get("sentences", []),
                "Path": item.get("path", ""),
            })
            
            if i + 1 >= max_records:
                break

    return pd.DataFrame(results)

def plot_duration_distribution(df):
    """Plots the distribution of video durations."""
    if "Duration" not in df.columns or df["Duration"].isna().all():
        logging.warning("No valid duration data to plot.")
        return
    
    plt.figure(figsize=(10, 5))
    sns.histplot(df["Duration"].dropna(), bins=20, kde=True, edgecolor="black")
    plt.xlabel("Duration (seconds)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Video Durations")
    plt.show()

# File Path
json_path = r'C:\Users\yashM\Downloads\OneDrive_1_1-26-2025\video_chapters_tr_youtube.json'

# Process data
df_videos = validate_youtube_data_sample(json_path, max_records=100)
logging.info(f"Loaded {df_videos.shape[0]} records.")

# Data Overview
logging.info(df_videos.info())
logging.info(df_videos.head())

# Plot
plot_duration_distribution(df_videos)

# Summary Stats
logging.info("\nSummary Statistics:\n" + str(df_videos.describe()))
