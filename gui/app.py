import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import time
import sys
import os
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config
from utils.video import VideoInput
from detector.detector import ObjectDetector
from detector.tracker import ObjectTracker
from detector.classifier import ObjectClassifier
from processing.object_buffer import ObjectAggregator
from processing.counting import LineCounter
from processing.queue_manager import QueueManager
from utils.drawing import draw_boxes, draw_counting_line, draw_info
from gui.widgets import QueueVisualizer, LogPanel, ControlPanel

class App:
    def __init__(self, root, queue_manager):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.queue_manager = queue_manager
        
        # Initialize components
        self.video = VideoInput(source=config.CAMERA_ID, width=config.FRAME_WIDTH, height=config.FRAME_HEIGHT, fps=config.FPS)
        # We use tracker which loads the model. Detector is implicitly used by tracker.
        self.tracker = ObjectTracker() 
        self.classifier = ObjectClassifier()
        self.aggregator = ObjectAggregator()
        self.line_counter = LineCounter(width=config.FRAME_WIDTH, height=config.FRAME_HEIGHT)
        
        self.running = False
        self.od_enabled = True
        self.class_enabled = True
        self.save_crops_enabled = False
        
        # GUI Layout
        self.setup_ui()
        
        # Start update loop
        self.root.after(config.GUI_REFRESH_INTERVAL, self.update_gui)
        
        # Auto-start camera
        self.start_camera()

    def setup_ui(self):
        # Main container using PanedWindow for resizing
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left: Video Feed
        self.video_frame = ttk.Frame(self.paned_window)
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.paned_window.add(self.video_frame, weight=3) # Give more space to video
        
        # Right: Controls & Info
        right_panel = ttk.Frame(self.paned_window, width=300)
        self.paned_window.add(right_panel, weight=1)
        
        # Controls
        callbacks = {
            'toggle_od': self.toggle_od,
            'toggle_class': self.toggle_class,
            'manual_pop': self.manual_pop,
            'clear_queue': self.clear_queue,
            'toggle_save_crops': self.toggle_save_crops,
            'clear_logs': self.clear_logs
        }
        self.controls = ControlPanel(right_panel, callbacks)
        self.controls.pack(fill=tk.X, pady=5, padx=5)
        
        # Queue Visualizer
        self.queue_viz = QueueVisualizer(right_panel)
        self.queue_viz.pack(fill=tk.X, pady=5, padx=5)
        
        # Logs
        self.logs = LogPanel(right_panel)
        self.logs.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        self.log("System initialized.")

    def log(self, msg):
        self.logs.log(msg)
        print(msg)

    def start_camera(self):
        if not self.running:
            self.video.start()
            self.running = True
            self.log("Camera started.")

    def stop_camera(self):
        if self.running:
            self.running = False
            self.video.stop()
            self.log("Camera stopped.")

    def toggle_od(self, value):
        self.od_enabled = value
        state = "enabled" if value else "disabled"
        self.log(f"Object Detection {state}.")

    def toggle_class(self, value):
        self.class_enabled = value
        state = "enabled" if value else "disabled"
        self.log(f"Classification {state}.")

    def toggle_save_crops(self, value):
        self.save_crops_enabled = value
        self.log(f"Save All Crops set to: {value}")

    def manual_pop(self):
        item = self.queue_manager.pop(block=False)
        if item:
            self.log(f"Popped: ID {item['id']} ({item['label']})")
        else:
            self.log("Queue is empty.")

    def clear_queue(self):
        self.queue_manager.clear()
        self.log("Queue cleared.")

    def clear_logs(self):
        # Clear logs/crops and logs/non_orange
        dirs_to_clear = [
            os.path.join("logs", "crops"),
            config.NON_ORANGE_LOG_DIR
        ]
        
        for d in dirs_to_clear:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                    os.makedirs(d, exist_ok=True)
                except Exception as e:
                    self.log(f"Error clearing {d}: {e}")
        
        self.log("Logs cleared (images deleted).")

    def update_gui(self):
        if self.running:
            frame = self.video.read()
            if frame is None:
                pass
            else:
                # Only process if OD is enabled
                if self.od_enabled:
                    # 1. Tracking
                    results = self.tracker.track(frame)
                    
                    # 2. Process tracks
                    if results and results[0].boxes and results[0].boxes.id is not None:
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        ids = results[0].boxes.id.cpu().numpy().astype(int)
                        clss = results[0].boxes.cls.cpu().numpy().astype(int)
                        names = results[0].names
                        
                        for box, track_id, cls in zip(boxes, ids, clss):
                            # Crop object
                            x1, y1, x2, y2 = box.astype(int)
                            h, w = frame.shape[:2]
                            x1, y1 = max(0, x1), max(0, y1)
                            x2, y2 = min(w, x2), min(h, y2)
                            
                            crop = frame[y1:y2, x1:x2]
                            if crop.size == 0:
                                continue
                            
                            # Check if new track (for logging)
                            is_new = track_id not in self.aggregator.buffers
                            
                            # Update buffer
                            buf = self.aggregator.update(track_id, crop)
                            
                            if is_new:
                                # Set class name
                                class_name = names[cls]
                                buf.od_class_name = class_name
                            
                            # Logic: Save Non-Orange ALWAYS
                            if buf.od_class_name != "orange":
                                folder_name = f"{buf.od_class_name}_{track_id}"
                                folder_path = os.path.join(config.NON_ORANGE_LOG_DIR, folder_name)
                                os.makedirs(folder_path, exist_ok=True)
                                
                                timestamp = int(time.time() * 1000)
                                img_name = f"{timestamp}.jpg"
                                cv2.imwrite(os.path.join(folder_path, img_name), crop)

                            # Save crop if enabled (for oranges or everything if enabled)
                            if self.save_crops_enabled:
                                folder_name = f"{buf.od_class_name}_{track_id}"
                                folder_path = os.path.join("logs", "crops", folder_name)
                                os.makedirs(folder_path, exist_ok=True)
                                
                                timestamp = int(time.time() * 1000)
                                img_name = f"{timestamp}.jpg"
                                cv2.imwrite(os.path.join(folder_path, img_name), crop)

                            # Run classification if enabled
                            if self.class_enabled and self.classifier.model:
                                preds = self.classifier.classify_batch([crop])
                                if preds:
                                    label_id, conf = preds[0]
                                    buf.update_classification(label_id)
                            
                            # Check line crossing (ONLY FOR COUNTING)
                            centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
                            prev_centroid = getattr(buf, 'last_centroid', None)
                            buf.last_centroid = centroid
                            
                            if self.line_counter.check_crossing(track_id, centroid, prev_centroid):
                                label = "rotten" if buf.classification_result == 1 else "fresh"
                                self.line_counter.increment(label)

                    # 3. Cleanup & Exit Logs
                    removed_buffers = self.aggregator.cleanup()
                    for buf in removed_buffers:
                        # Add to queue
                        label = "rotten" if buf.classification_result == 1 else "fresh"
                        item = {
                            "id": buf.track_id,
                            "label": label,
                            "timestamp": time.time()
                        }
                        self.queue_manager.push(item)

                        # Exit Logs
                        self.log("_______________________________________")
                        self.log(f"Object {buf.track_id} exited.")
                        self.log(f"Frames seen: {buf.total_frames}")
                        self.log(f"Detected class: {buf.od_class_name}")
                        
                        if buf.od_class_name == "orange":
                            if buf.is_rotten:
                                 self.log(f"Classification: rotten ({buf.rotten_frames_count} frames)")
                            else:
                                 self.log(f"Classification: fresh ({buf.fresh_frames_count} frames)")
                        else:
                            self.log("(no classification)")

                    # 4. Drawing
                    frame = draw_boxes(frame, results, self.aggregator.buffers)
                    frame = draw_counting_line(frame, self.line_counter)
                    frame = draw_info(frame, self.line_counter.get_counts())
                
                # 5. Display
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        
        # Update Queue Visualizer
        items = self.queue_manager.get_all()
        self.queue_viz.update_list(items)

        self.root.after(config.GUI_REFRESH_INTERVAL, self.update_gui)

    def on_close(self):
        self.stop_camera()
        self.root.destroy()
