import time
import sys
import os
from collections import deque

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class TrackBuffer:
    """
    Stores data for a single tracked object.
    """
    def __init__(self, track_id, max_size=100):
        self.track_id = track_id
        self.crops = deque(maxlen=max_size)
        self.last_seen = time.time()
        self.finalized = False
        self.classification_result = None # 1 (rotten) or 0 (fresh)
        self.is_rotten = False # Flag if ANY rotten frame is seen
        
        # New stats
        self.od_class_name = "unknown"
        self.total_frames = 0
        self.fresh_frames_count = 0
        self.rotten_frames_count = 0

    def add_crop(self, crop):
        self.crops.append(crop)
        self.last_seen = time.time()
        self.total_frames += 1

    def update_classification(self, label_id):
        """
        Update the running classification status.
        Decision rule: If ANY crop is rotten (1), the object is rotten.
        """
        # Assuming 0 is fresh, 1 is rotten (updated config)
        if label_id == 1:
            self.is_rotten = True
            self.rotten_frames_count += 1
        else:
            self.fresh_frames_count += 1
        
        # Current status
        self.classification_result = 1 if self.is_rotten else 0

class ObjectAggregator:
    """
    Manages TrackBuffers for all active objects.
    """
    def __init__(self):
        self.buffers = {} # track_id -> TrackBuffer

    def update(self, track_id, crop):
        """
        Add a new crop for a track ID.
        """
        if track_id not in self.buffers:
            self.buffers[track_id] = TrackBuffer(track_id, max_size=config.MAX_BUFFER_SIZE)
        
        self.buffers[track_id].add_crop(crop)
        return self.buffers[track_id]

    def get_buffer(self, track_id):
        return self.buffers.get(track_id)

    def cleanup(self, timeout=None):
        """
        Remove tracks that haven't been seen for 'timeout' seconds.
        Returns a list of removed TrackBuffers (so we can finalize them if needed).
        """
        timeout = timeout if timeout is not None else config.TRACK_TIMEOUT
        now = time.time()
        to_remove = []
        
        for tid, buf in self.buffers.items():
            if now - buf.last_seen > timeout:
                to_remove.append(tid)
        
        removed_buffers = []
        for tid in to_remove:
            removed_buffers.append(self.buffers.pop(tid))
            
        return removed_buffers

    def finalize_track(self, track_id):
        """
        Mark a track as finalized (e.g. when it crosses the line).
        """
        if track_id in self.buffers:
            self.buffers[track_id].finalized = True
            return self.buffers[track_id]
        return None
