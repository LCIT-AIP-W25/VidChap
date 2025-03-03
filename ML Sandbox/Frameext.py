import cv2
import numpy as np
from sklearn.cluster import KMeans\

cap = cv2.VideoCapture("test.mp4")  # Load the video file

frame_count = 0  # Keep track of the number of frames processed
while cap.isOpened():  # Loop until the video ends
    ret, frame = cap.read()  # Read a frame from the video
    if not ret:  # If no frame is returned (end of video), break the loop
        break
    cv2.imwrite(f"frames/frame_{frame_count}.jpg", frame)  # Save the frame as an image
    frame_count += 1  # Increment frame count

cap.release()  # Release video file from memory
cv2.destroyAllWindows()  # Close any OpenCV windows

# Load a sample image (simulating a video frame)
frame = cv2.imread("frames/frame_10.jpg")

# Convert image to a feature vector (flatten pixels)
pixels = frame.reshape(-1, 3)  # Convert to (num_pixels, 3) for clustering

# Apply K-Means Clustering
kmeans = KMeans(n_clusters=3)  # Try clustering into 3 groups
kmeans.fit(pixels)

# Assign new colors based on clusters
segmented_img = kmeans.cluster_centers_[kmeans.labels_].reshape(frame.shape)
segmented_img = np.uint8(segmented_img)  # Convert back to image format

cv2.imshow("Segmented Frame", segmented_img)
cv2.waitKey(0)
cv2.destroyAllWindows()


#Color Histogram Difference -- compares the color distribution of two frames.


def get_histogram(frame):
    """Compute color histogram for a frame."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Convert to HSV color space
    hist = cv2.calcHist([hsv], [0], None, [256], [0, 256])  # Compute histogram for Hue channel
    cv2.normalize(hist, hist)  # Normalize histogram values
    return hist.flatten()

# Load two consecutive frames
frame1 = cv2.imread("frames/frame_10.jpg")
frame2 = cv2.imread("frames/frame_11.jpg")

# Compute histograms
hist1 = get_histogram(frame1)
hist2 = get_histogram(frame2)

# Compute difference using correlation
difference = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)  # 1 means identical else different
print(f"Histogram Similarity: {difference}")

# code for edge detection

def get_edges(frame):
    """Apply Canny Edge Detection to a frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    edges = cv2.Canny(gray, 100, 200)  # Detect edges
    return edges

# Load a frame
frame = cv2.imread("frames/frame_10.jpg")
edges = get_edges(frame)

# Show the edges
cv2.imshow("Edges", edges)
cv2.waitKey(0)
cv2.destroyAllWindows()

'''
Code for Optical Flow (Lucas-Kanade Method)
 need to be refined 
 
def get_optical_flow(prev_frame, next_frame):
    """Compute Optical Flow between two frames."""
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    return np.linalg.norm(flow)  # Return magnitude of motion

# Load two consecutive frames
frame1 = cv2.imread("frames/frame_10.jpg")
frame2 = cv2.imread("frames/frame_11.jpg")

motion_magnitude = get_optical_flow(frame1, frame2)
print(f"Motion Magnitude: {motion_magnitude}")
'''

