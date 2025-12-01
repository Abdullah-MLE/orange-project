import cv2
import os
import datetime
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

# Currently unused but kept if needed for non-orange saving
def save_crop(crop, track_id, label, is_non_orange=False):
    """
    Save a cropped image to disk.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}_ID{track_id}_{label}.jpg"
    
    if is_non_orange:
        path = os.path.join(config.NON_ORANGE_LOG_DIR, filename)
        try:
            cv2.imwrite(path, crop)
        except Exception as e:
            print(f"Error saving crop: {e}")
