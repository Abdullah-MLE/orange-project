from ultralytics import YOLO
import sys
import os

# Add project root to path to allow importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class ObjectTracker:
    """
    Wrapper for YOLOv8 tracking (BoT-SORT / ByteTrack).
    """
    def __init__(self, model_path=None, tracker_type=None):
        self.model_path = model_path if model_path else config.MODEL_OD_PATH
        self.tracker_type = tracker_type if tracker_type else config.TRACKER_TYPE
        
        # We use the same model as detector, or load a new instance.
        # To save memory, we could pass the model instance, but for simplicity/modularity
        # we'll load it here or allow passing it.
        # For this implementation, let's assume we load it here to be self-contained 
        # or we could accept an existing ObjectDetector instance.
        # Let's load it to be safe and simple.
        print(f"Loading Tracker Model from: {self.model_path}")
        self.model = YOLO(self.model_path)

    def track(self, frame, conf=None, iou=None, persist=True):
        """
        Run tracking on a frame.
        persist=True is crucial for video tracking to maintain IDs.
        """
        conf = conf if conf is not None else config.CONF_THRESHOLD
        iou = iou if iou is not None else config.IOU_THRESHOLD
        
        # tracker argument expects a yaml file or name like 'bytetrack.yaml'
        # Ultralytics comes with 'bytetrack.yaml' and 'botsort.yaml'
        tracker_config = f"{self.tracker_type}.yaml"
        
        results = self.model.track(
            source=frame,
            conf=conf,
            iou=iou,
            classes=config.DETECT_CLASS_IDS,
            persist=persist,
            tracker=tracker_config,
            verbose=False
        )
        return results

    def update_tracker_type(self, tracker_type):
        self.tracker_type = tracker_type
