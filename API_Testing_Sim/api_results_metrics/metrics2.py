import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_json(file_path):
    """Load JSON data from a given file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def parse_data(data):
    """Parse chapter names and timestamps from the JSON data."""
    chapters = {}
    for video_id, content in data.items():
        chapter_lines = content.split("\n")
        for line in chapter_lines:
            if "chapter :" in line:
                # Extract chapter name and timestamps using regex
                match = re.search(r"chapter : (.+) (\d+\.\d+) (\d+\.\d+)", line)
                if match:
                    chapter_name = match.group(1).strip()
                    start_time = float(match.group(2))
                    end_time = float(match.group(3))

                    if video_id not in chapters:
                        chapters[video_id] = []
                    chapters[video_id].append({"name": chapter_name, "start": start_time, "end": end_time})
    return chapters

def calculate_cosine_similarity(chapters1, chapters2):
    """Calculate cosine similarity between chapter names using TF-IDF embeddings."""
    names1 = [ch['name'] for ch in chapters1]
    names2 = [ch['name'] for ch in chapters2]

    vectorizer = TfidfVectorizer().fit(names1 + names2)
    vectors1 = vectorizer.transform(names1)
    vectors2 = vectorizer.transform(names2)

    similarity_matrix = cosine_similarity(vectors1, vectors2)
    return similarity_matrix


def calculate_iou(start1, end1, start2, end2):
    """Calculate Intersection over Union (IoU) for timestamps."""
    intersection = max(0, min(end1, end2) - max(start1, start2))
    union = (end1 - start1) + (end2 - start2) - intersection
    return intersection / union if union != 0 else 0


def compare_files(file1_path, file2_path):
    """Main function to compare chapter names and timestamps between two files."""
    # Load data
    data1 = load_json(file1_path)
    data2 = load_json(file2_path)

    # Parse data
    chapters1 = parse_data(data1)
    chapters2 = parse_data(data2)

    results = {}

    # Compare each video
    for video_id in chapters1.keys() & chapters2.keys():
        chapters_file1 = chapters1[video_id]
        chapters_file2 = chapters2[video_id]

        # Cosine similarity for chapter names
        name_similarity = calculate_cosine_similarity(chapters_file1, chapters_file2)

        # IoU for timestamps
        iou_scores = []
        for ch1 in chapters_file1:
            best_iou = 0
            for ch2 in chapters_file2:
                iou = calculate_iou(ch1['start'], ch1['end'], ch2['start'], ch2['end'])
                best_iou = max(best_iou, iou)
            iou_scores.append(best_iou)

        avg_name_similarity = np.mean(np.max(name_similarity, axis=1)) if name_similarity.size > 0 else 0
        avg_iou_score = np.mean(iou_scores) if iou_scores else 0

        results[video_id] = {
            "avg_chapter_name_similarity": avg_name_similarity,
            "avg_timestamp_iou": avg_iou_score
        }

    return results


def main():
    """Run the comparison and print the results."""
    file1_path = "dataset_sample.json"  # Update with actual file path
    file2_path = "output_sample.json"  # Update with actual file path

    results = compare_files(file1_path, file2_path)

    # Print results
    for video_id, metrics in results.items():
        print(f"Video ID: {video_id}")
        print(f"  Average Chapter Name Similarity: {metrics['avg_chapter_name_similarity']:.4f}")
        print(f"  Average Timestamp IoU: {metrics['avg_timestamp_iou']:.4f}")
        print()

    # Create a DataFrame for easier analysis and plotting
    video_ids = []
    chapter_similarities = []
    timestamp_ious = []

    # Populate the lists with the results
    for video_id, metrics in results.items():
        video_ids.append(video_id)
        chapter_similarities.append(metrics['avg_chapter_name_similarity'])
        timestamp_ious.append(metrics['avg_timestamp_iou'])

    # Create DataFrame
    df = pd.DataFrame({
        'video_id': video_ids,
        'chapter_similarity': chapter_similarities,
        'timestamp_iou': timestamp_ious
    })

    # === Basic Stats ===
    print("\nBasic Statistics:\n", df.describe())

    # === Visualization Config ===
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 8))

    # === Distribution of Chapter Name Similarity ===
    plt.subplot(2, 2, 1)
    sns.histplot(df['chapter_similarity'], bins=10, kde=True, color='skyblue')
    plt.title("Distribution of Chapter Name Similarity")

    # === Distribution of Timestamp IoU ===
    plt.subplot(2, 2, 2)
    sns.histplot(df['timestamp_iou'], bins=10, kde=True, color='lightcoral')
    plt.title("Distribution of Timestamp IoU")

    # === Correlation Scatterplot ===
    plt.subplot(2, 2, 3)
    sns.scatterplot(x='chapter_similarity', y='timestamp_iou', data=df, color='purple')
    plt.title("Correlation Between Chapter Similarity and IoU")

    # === Boxplot for Chapter Name Similarity and IoU ===
    plt.subplot(2, 2, 4)
    sns.boxplot(data=df[['chapter_similarity', 'timestamp_iou']], palette='coolwarm')
    plt.title("Boxplot of Chapter Name Similarity and Timestamp IoU")

    plt.tight_layout()
    plt.show()

    # === Top 5 & Bottom 5 Performers ===
    top_5_chapter_sim = df.sort_values(by='chapter_similarity', ascending=False).head(5)
    bottom_5_chapter_sim = df.sort_values(by='chapter_similarity', ascending=True).head(5)

    top_5_iou = df.sort_values(by='timestamp_iou', ascending=False).head(5)
    bottom_5_iou = df.sort_values(by='timestamp_iou', ascending=True).head(5)

    print("\n🔥 Top 5 Chapter Name Similarities:\n", top_5_chapter_sim)
    print("\n❄️ Bottom 5 Chapter Name Similarities:\n", bottom_5_chapter_sim)
    print("\n🚀 Top 5 Timestamp IoU Scores:\n", top_5_iou)
    print("\n⏳ Bottom 5 Timestamp IoU Scores:\n", bottom_5_iou)

if __name__ == "__main__":
    main()