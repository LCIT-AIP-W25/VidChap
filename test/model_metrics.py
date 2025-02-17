import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_cosine_similarity(name1, name2, model):
    embeddings = model.encode([name1, name2])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def iou_time_overlap(pred_start, pred_end, actual_start, actual_end):
    intersection = max(0, min(pred_end, actual_end) - max(pred_start, actual_start))
    union = max(pred_end, actual_end) - min(pred_start, actual_start)
    return intersection / union if union > 0 else 0

def evaluate(pred_file, actual_file):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    predictions = load_json(pred_file)
    actuals = load_json(actual_file)
    
    total_cosine = 0
    total_iou = 0
    matched_count = 0
    
    for pred in predictions:
        best_match = None
        best_score = 0
        
        for actual in actuals:
            cosine_sim = calculate_cosine_similarity(pred['chapter_name'], actual['chapter_name'], model)
            iou_score = iou_time_overlap(pred['start_time'], pred['end_time'], actual['start_time'], actual['end_time'])
            
            combined_score = (cosine_sim + iou_score) / 2  # Weighted equally
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = actual
        
        if best_match:
            total_cosine += calculate_cosine_similarity(pred['chapter_name'], best_match['chapter_name'], model)
            total_iou += iou_time_overlap(pred['start_time'], pred['end_time'], best_match['start_time'], best_match['end_time'])
            matched_count += 1
    
    avg_cosine = total_cosine / matched_count if matched_count else 0
    avg_iou = total_iou / matched_count if matched_count else 0
    
    print(f"Average Cosine Similarity: {avg_cosine:.4f}")
    print(f"Average IoU Score: {avg_iou:.4f}")


evaluate('output.json', 'converted_file.json')


# Interim Fixes needs to be done before evaluation

# import json

# def load_json(filename):
#     with open(filename, 'r', encoding='utf-8') as file:
#         try:
#             data = json.load(file)
#             return data
#         except json.JSONDecodeError as e:
#             print(f"Error loading {filename}: {e}")
#             return None


# pred_data = load_json(predicted_file)
# actual_data = load_json(actual_file)

# if pred_data is None or actual_data is None:
#     print("Error: Could not load JSON files.")
#     exit()

# for pred, actual in zip(pred_data, actual_data):
#     print(f"Processing: {pred}, {actual}")  # Debugging


# import json

# with open("output.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     print(type(data), data[:5])  # Print the first 5 elements

# for item in pred_data:
#     print(item)  # Check structure
