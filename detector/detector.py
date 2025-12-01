from ultralytics import YOLO
import sys
import os

# Add project root to path to allow importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class ObjectDetector:
    """
    Wrapper for YOLOv8 object detection model.
    """
    def __init__(self, model_path=None):
        self.model_path = model_path if model_path else config.MODEL_OD_PATH
        print(f"Loading Object Detection Model from: {self.model_path}")
        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

    def detect(self, frame, conf=None, iou=None):
        """
        Run object detection on a single frame.
        Returns the results object from Ultralytics.
        """
        conf = conf if conf is not None else config.CONF_THRESHOLD
        iou = iou if iou is not None else config.IOU_THRESHOLD
        
        # classes=config.DETECT_CLASS_IDS filters for oranges only
        results = self.model.predict(
            source=frame,
            conf=conf,
            iou=iou,
            classes=config.DETECT_CLASS_IDS,
            verbose=False
        )
        return results
