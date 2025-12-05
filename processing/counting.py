import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class LineCounter:
    """
    Handles counting objects that cross a defined line.
    """
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.orientation = config.LINE_ORIENTATION
        self.position_ratio = config.LINE_POSITION
        self.direction = config.COUNT_DIRECTION
        
        # Calculate pixel position of the line
        if self.orientation == "horizontal":
            self.line_pos = int(self.height * self.position_ratio)
        else:
            self.line_pos = int(self.width * self.position_ratio)
            
        # Keep track of objects that have already been counted
        self.counted_ids = set()
        
        # Counters
        self.counts = {
            "fresh": 0,
            "rotten": 0,
            "non_orange": 0,
            "total": 0
        }

    def check_crossing(self, track_id, centroid, prev_centroid):
        """
        Check if an object crossed the line in the configured direction.
        centroid: (x, y)
        prev_centroid: (x, y) - can be None if new object
        """
        if track_id in self.counted_ids:
            return False

        if prev_centroid is None:
            return False

        cx, cy = centroid
        px, py = prev_centroid
        
        crossed = False
        
        if self.orientation == "horizontal":
            # Line is at Y = self.line_pos
            if self.direction == "down":
                # Moving from < line_pos to > line_pos
                if py <= self.line_pos and cy > self.line_pos:
                    crossed = True
            elif self.direction == "up":
                # Moving from > line_pos to < line_pos
                if py >= self.line_pos and cy < self.line_pos:
                    crossed = True
                    
        elif self.orientation == "vertical":
            # Line is at X = self.line_pos
            if self.direction == "right":
                if px <= self.line_pos and cx > self.line_pos:
                    crossed = True
            elif self.direction == "left":
                if px >= self.line_pos and cx < self.line_pos:
                    crossed = True
                    
        if crossed:
            self.counted_ids.add(track_id)
            return True
            
        return False

    def increment(self, label):
        """
        Increment counter based on label.
        label: "fresh", "rotten", etc.
        """
        self.counts["total"] += 1
        if label in self.counts:
            self.counts[label] += 1
        else:
            # Fallback for unknown labels, treat as non_orange or ignore
            if label not in ["fresh", "rotten"]:
                 self.counts["non_orange"] += 1

    def get_counts(self):
        return self.counts

    def set_line_position(self, ratio):
        self.position_ratio = ratio
        if self.orientation == "horizontal":
            self.line_pos = int(self.height * self.position_ratio)
        else:
            self.line_pos = int(self.width * self.position_ratio)
