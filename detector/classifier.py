from ultralytics import YOLO
import sys
import os
import torch

# Add project root to path to allow importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class ObjectClassifier:
    """
    Wrapper for the classification model (Fresh vs Rotten).
    """
    def __init__(self, model_path=None):
        self.model_path = model_path if model_path else config.MODEL_CLASS_PATH
        print(f"Loading Classification Model from: {self.model_path}")
        self.model = YOLO(self.model_path)

    def classify_batch(self, crops):
        """
        Run classification on a batch of cropped images.
        crops: List of numpy arrays (images).
        Returns: List of result objects or labels.
        """
        if not self.model or not crops:
            return []

        # Run inference
        # verbose=False to reduce log noise
        results = self.model.predict(source=crops, verbose=False, batch=len(crops))
        
        # Extract class indices/names
        # Assuming binary classification: 0=rotten, 1=fresh (or defined in config)
        predictions = []
        for r in results:
            # probs is a tensor, get the top class
            top_class_id = r.probs.top1
            conf = r.probs.top1conf.item()
            predictions.append((top_class_id, conf))
            
        return predictions
