import json
import numpy as np

def calculate_iou(pred_interval, gt_interval):
    """Calculates IoU between two time intervals."""
    start_pred, end_pred = pred_interval
    start_gt, end_gt = gt_interval

    # Intersection (Overlap)
    intersection = max(0, min(end_pred, end_gt) - max(start_pred, start_gt))

    # Union (Total Duration Covered)
    union = (end_pred - start_pred) + (end_gt - start_gt) - intersection

    # Avoid division by zero
    if union == 0:
        return 0.0

    return intersection / union

def evaluate_iou(pred_chapters, gt_chapters):
    """Calculates the average IoU for predicted and ground truth chapters."""
    iou_scores = []

    for pred_scene in pred_chapters:
        pred_interval = (pred_scene['start'], pred_scene['end'])

        # Find the closest matching ground truth scene
        best_iou = 0.0
        for gt_scene in gt_chapters:
            gt_interval = (gt_scene['start'], gt_scene['end'])
            iou_score = calculate_iou(pred_interval, gt_interval)
            best_iou = max(best_iou, iou_score)

        iou_scores.append(best_iou)

    # Average IoU Score
    avg_iou = np.mean(iou_scores)
    return avg_iou

def load_chapters(file_path):
    """Loads chapter data from JSON."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['chapters']

if __name__ == "__main__":
    # Load predicted and ground truth chapters
    predicted_chapters = load_chapters("predicted_chapters.json")
    ground_truth_chapters = load_chapters("ground_truth_chapters.json")

    # Evaluate IoU
    avg_iou = evaluate_iou(predicted_chapters, ground_truth_chapters)
    print(f"Average IoU Score: {avg_iou:.2f}")
