import os

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================
# Path to the YOLOv8n object detection model.
# This model is responsible for detecting oranges in the frame.
MODEL_OD_PATH = "models/yolov8n.pt"

# Path to the custom classification model.
# This model classifies cropped orange images as 'fresh' or 'rotten'.
MODEL_CLASS_PATH = "models/best.pt"

# Confidence threshold for object detection (0.0 - 1.0).
# Detections with confidence below this value will be ignored.
CONF_THRESHOLD = 0

# IoU threshold for Non-Maximum Suppression (0.0 - 1.0).
IOU_THRESHOLD = 0.45

# Allowed class IDs for detection.
# Assuming 'orange' is class 49 in COCO dataset (used by yolov8n).
# If using a custom trained OD model, adjust this ID.
# Set to None to detect ALL classes (e.g. rocks, cups, etc.)
DETECT_CLASS_IDS = None 

# =============================================================================
# CAMERA & VIDEO CONFIGURATION
# =============================================================================
# Camera ID or video file path.
# Use 0 for the default webcam, 1 for external, or a path to a video file.
CAMERA_ID = "test1.mp4"

# Desired frame width and height.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Target FPS for the camera capture.
FPS = 30

# =============================================================================
# TRACKER CONFIGURATION
# =============================================================================
# Tracker type: 'bytetrack' or 'botsort'.
# BoT-SORT is generally more robust but slightly slower. ByteTrack is faster.
TRACKER_TYPE = "botsort"

# Tracker configuration file (optional, usually handled by ultralytics default).
# If None, uses default settings.
TRACKER_CONFIG = "botsort.yaml" 

# =============================================================================
# COUNTING LINE CONFIGURATION
# =============================================================================
# Orientation of the counting line: 'horizontal' or 'vertical'.
LINE_ORIENTATION = "horizontal"

# Position of the line as a percentage of frame dimension (0.0 - 1.0).
# If horizontal, this is Y position (0.5 = middle).
# If vertical, this is X position.
LINE_POSITION = 0.5

# Color of the counting line (B, G, R).
LINE_COLOR = (0, 0, 255)  # Red

# Thickness of the counting line in pixels.
LINE_THICKNESS = 2

# Direction of movement to count.
# For horizontal line: 'down' (y increases) or 'up' (y decreases).
# For vertical line: 'right' (x increases) or 'left' (x decreases).
COUNT_DIRECTION = "up"

# =============================================================================
# CLASSIFICATION & BUFFER CONFIGURATION
# =============================================================================
# Maximum number of crop images to store per tracked object.
MAX_BUFFER_SIZE = 100

# Timeout in seconds to keep a track alive after it disappears from frame.
# This helps handle temporary occlusions.
TRACK_TIMEOUT = 2.0

# Batch size for classifier inference.
CLASSIFIER_BATCH_SIZE = 8

# Decision rule: If ANY crop is 'rotten', the object is 'rotten'.
# Class labels for the classifier model.
# Swapped based on user feedback (0=fresh, 1=rotten)
CLASS_LABELS = {0: "fresh", 1: "rotten"}

# =============================================================================
# LOGGING & SAVING CONFIGURATION
# =============================================================================
# Directory to save crops of non-orange detections.
NON_ORANGE_LOG_DIR = "logs/non_orange"

# Toggle to save non-orange crops.
SAVE_NON_ORANGE = True

# =============================================================================
# QUEUE CONFIGURATION
# =============================================================================
# Maximum size of the queue.
QUEUE_MAX_SIZE = 1000

# =============================================================================
# GUI CONFIGURATION
# =============================================================================
# Window title.
WINDOW_TITLE = "Orange Detection System"

# Refresh rate for GUI updates in milliseconds.
GUI_REFRESH_INTERVAL = 30

# Colors for overlays (B, G, R).
COLOR_FRESH = (0, 255, 0)   # Green
COLOR_ROTTEN = (0, 0, 255)  # Red
COLOR_UNKNOWN = (255, 255, 0) # Cyan/Yellowish
COLOR_TEXT = (255, 255, 255) # White

# Create directories if they don't exist
os.makedirs(NON_ORANGE_LOG_DIR, exist_ok=True)
