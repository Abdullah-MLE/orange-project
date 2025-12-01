import cv2
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

def draw_boxes(frame, tracks, buffers):
    """
    Draw bounding boxes, centers, and IDs on the frame.
    tracks: result from tracker.track()
    buffers: ObjectAggregator.buffers (to get classification status)
    """
    if tracks[0].boxes is None or tracks[0].boxes.id is None:
        return frame

    boxes = tracks[0].boxes.xyxy.cpu().numpy().astype(int)
    ids = tracks[0].boxes.id.cpu().numpy().astype(int)
    
    for box, track_id in zip(boxes, ids):
        x1, y1, x2, y2 = box
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Determine color based on classification
        color = config.COLOR_UNKNOWN
        label_text = f"ID: {track_id}"
        
        if track_id in buffers:
            buf = buffers[track_id]
            # Use OD class name if available
            if hasattr(buf, 'od_class_name'):
                label_text = f"{buf.od_class_name} {track_id}"
            
            # Keep color coding for Fresh/Rotten if it's an orange?
            # User said: "not show fresh or rotten, show class name from OD model"
            # But maybe color can still indicate it?
            # User didn't explicitly say remove color coding, just the text.
            # "مش عايز يكون ظاهر على البرتقاله اسم الكلاس fresh او rotten لا عايز يكون مكتوب اسم الكلاس اللي موديل ال od عرفها بيه"
            # (I don't want the class name fresh or rotten to appear on the orange, no I want the class name that the OD model knew it by to be written)
            
            if buf.classification_result == 0:
                color = config.COLOR_FRESH
            elif buf.classification_result == 1:
                color = config.COLOR_ROTTEN
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw center circle
        cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)
        
        # Draw label
        cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
    return frame

def draw_counting_line(frame, line_counter):
    """
    Draw the counting line.
    """
    if line_counter.orientation == "horizontal":
        cv2.line(frame, (0, line_counter.line_pos), (frame.shape[1], line_counter.line_pos), config.LINE_COLOR, config.LINE_THICKNESS)
    else:
        cv2.line(frame, (line_counter.line_pos, 0), (line_counter.line_pos, frame.shape[0]), config.LINE_COLOR, config.LINE_THICKNESS)
    return frame

def draw_info(frame, counts):
    """
    Draw counters on the frame.
    """
    text = f"Total: {counts['total']} | Fresh: {counts['fresh']} | Rotten: {counts['rotten']}"
    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, config.COLOR_TEXT, 2)
    return frame
