import customtkinter as ctk
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
from utils.drawing import draw_boxes, draw_counting_line, draw_info
from gui.widgets import LogPanel, ControlPanel, StatsPanel
from hardware.serial_comm import SerialCommunicator

# Set theme and color
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set window size and make it resizable
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Set consistent background color
        self.root.configure(fg_color=("#1a1a1a", "#0f0f0f"))
        
        self.app_running = True
        self.after_id = None
        self.belt_status = "Stopped"  # Initial status
        
        # Initialize components
        self.video = VideoInput(source=config.CAMERA_ID, width=config.FRAME_WIDTH, 
                               height=config.FRAME_HEIGHT, fps=config.FPS)
        self.tracker = ObjectTracker() 
        self.classifier = ObjectClassifier()
        self.aggregator = ObjectAggregator()
        self.line_counter = LineCounter(width=config.FRAME_WIDTH, height=config.FRAME_HEIGHT)
        
        # Initialize Serial
        self.serial = SerialCommunicator(port=config.SERIAL_PORT, baud_rate=config.BAUD_RATE)
        
        self.running = False
        self.od_enabled = True
        self.class_enabled = True
        self.save_crops_enabled = False
        
        # GUI Layout
        self.setup_ui()
        
        # Start update loop
        self.after_id = self.root.after(config.GUI_REFRESH_INTERVAL, self.update_gui)
        

        # Auto-start camera
        self.video.start()
        self.running = True
        self.log("Camera started successfully")
        self.update_status_bar()

    def setup_ui(self):
        # Main container with consistent color
        main_container = ctk.CTkFrame(self.root, fg_color=("#1a1a1a", "#0f0f0f"))
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create PanedWindow for resizable sections
        self.paned_window = ctk.CTkFrame(main_container, fg_color="transparent")
        self.paned_window.pack(fill="both", expand=True)
        
        # Configure grid for resizable panels
        self.paned_window.grid_columnconfigure(0, weight=3, minsize=600)
        self.paned_window.grid_columnconfigure(1, weight=0)  # Sash
        self.paned_window.grid_columnconfigure(2, weight=1, minsize=350)
        self.paned_window.grid_rowconfigure(0, weight=1)
        
        # ============= LEFT SIDE: VIDEO FEED =============
        video_container = ctk.CTkFrame(self.paned_window, corner_radius=15, 
                                      fg_color=("#242424", "#1a1a1a"))
        video_container.grid(row=0, column=0, sticky="nsew")
        
        # Video header with status info
        video_header = ctk.CTkFrame(video_container, height=70, corner_radius=0, 
                                   fg_color=("#2b2b2b", "#1a1a1a"))
        video_header.pack(fill="x", padx=0, pady=0)
        
        # Title
        title_label = ctk.CTkLabel(video_header, text="Live Video Feed", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(side="left", padx=20, pady=15)
        
        # Status bar on right
        self.status_container = ctk.CTkFrame(video_header, fg_color="transparent")
        self.status_container.pack(side="right", padx=20)
        
        # Camera type
        self.camera_type_label = ctk.CTkLabel(self.status_container, text="", 
                                             font=ctk.CTkFont(size=11))
        self.camera_type_label.pack(anchor="e", pady=2)
        
        # Belt status
        self.belt_status_frame = ctk.CTkFrame(self.status_container, fg_color="transparent")
        self.belt_status_frame.pack(anchor="e", pady=2)
        
        self.status_dot = ctk.CTkLabel(self.belt_status_frame, text="STATUS", 
                                      text_color="#fbbf24", 
                                      font=ctk.CTkFont(size=16))
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.belt_status_label = ctk.CTkLabel(self.belt_status_frame, text="Belt: Stopped", 
                                             text_color="#fbbf24",
                                             font=ctk.CTkFont(size=12, weight="bold"))
        self.belt_status_label.pack(side="left")
        
        # Video display area
        self.video_frame = ctk.CTkFrame(video_container, fg_color=("#1a1a1a", "#0f0f0f"))
        self.video_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ============= SASH (SEPARATOR) =============
        sash = ctk.CTkFrame(self.paned_window, width=10, cursor="sb_h_double_arrow",
                           fg_color=("#2b2b2b", "#1a1a1a"))
        sash.grid(row=0, column=1, sticky="ns", padx=5)
        
        # Bind sash for dragging
        sash.bind("<Button-1>", self.start_sash_drag)
        sash.bind("<B1-Motion>", self.on_sash_drag)
        
        # ============= RIGHT SIDE: CONTROLS & INFO =============
        right_container = ctk.CTkScrollableFrame(self.paned_window, corner_radius=15,
                                      fg_color=("#242424", "#1a1a1a"))
        right_container.grid(row=0, column=2, sticky="nsew")
        
        # Configure right container grid
        right_container.grid_rowconfigure(0, weight=0)  # Controls
        right_container.grid_rowconfigure(1, weight=0)  # Stats
        right_container.grid_rowconfigure(2, weight=1)  # Logs
        right_container.grid_columnconfigure(0, weight=1)
        
        # Controls Panel
        callbacks = {
            'toggle_od': self.toggle_od,
            'toggle_class': self.toggle_class,
            'toggle_save_crops': self.toggle_save_crops,
            'clear_logs': self.clear_logs,
            'start_conveyor_belt': self.start_conveyor_belt,
            'stop_conveyor_belt': self.stop_conveyor_belt,
            'toggle_logs': self.toggle_logs,
            'reset_hardware': self.reset_hardware
        }
        self.controls = ControlPanel(right_container, callbacks)
        self.controls.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Stats Panel
        self.stats_panel = StatsPanel(right_container)
        self.stats_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Logs Panel with scrollbar
        self.logs = LogPanel(right_container)
        self.logs.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        self.log("System initialized successfully")

    def start_sash_drag(self, event):
        self.sash_start_x = event.x_root
        self.left_width = self.paned_window.grid_columnconfigure(0)['minsize']

    def on_sash_drag(self, event):
        delta = event.x_root - self.sash_start_x
        current_weight_left = self.paned_window.grid_columnconfigure(0)['weight']
        current_weight_right = self.paned_window.grid_columnconfigure(2)['weight']
        
        # Adjust weights based on drag
        new_weight_left = max(2, current_weight_left + delta / 100)
        new_weight_right = max(1, current_weight_right - delta / 100)
        
        self.paned_window.grid_columnconfigure(0, weight=int(new_weight_left))
        self.paned_window.grid_columnconfigure(2, weight=int(new_weight_right))

    def get_camera_type(self):
        """Determine camera type from CAMERA_ID"""
        camera_id = str(config.CAMERA_ID)
        
        if camera_id == '0':
            return "Webcam"
        elif camera_id == '1':
            return "USB Camera"
        elif camera_id.endswith(('.mp4', '.avi', '.mkv', '.mov')):
            return f"Video: {os.path.basename(camera_id)}"
        else:
            return f"Camera: {camera_id}"

    def update_status_bar(self):
        """Update camera type and belt status"""
        # Update camera type
        camera_type = self.get_camera_type()
        self.camera_type_label.configure(text=camera_type)
        
        # Update belt status
        if self.belt_status == "Running":
            color = "#22c55e"  # Green
            self.belt_status_label.configure(text="Belt: Running", text_color=color)
            self.status_dot.configure(text_color=color)
        elif self.belt_status == "Stopped":
            color = "#ef4444"  # Red
            self.belt_status_label.configure(text="Belt: Stopped", text_color=color)
            self.status_dot.configure(text_color=color)
        elif self.belt_status == "Resetting":
            color = "#fbbf24"  # Yellow
            self.belt_status_label.configure(text="Belt: Resetting", text_color=color)
            self.status_dot.configure(text_color=color)

    def log(self, msg):
        self.logs.log(msg)
        print(msg)

    def start_conveyor_belt(self):
        self.serial.send_command("START")
        self.belt_status = "Running"
        self.update_status_bar()
        self.log("Conveyor belt started")

    def stop_conveyor_belt(self):
        self.serial.send_command("STOP")
        self.belt_status = "Stopped"
        self.update_status_bar()
        self.log("Conveyor belt stopped")

    def reset_hardware(self):
        self.serial.send_command("RESET")
        self.belt_status = "Resetting"
        self.update_status_bar()
        self.log("Hardware reset initiated")
        # After reset, belt should be stopped
        self.root.after(2000, lambda: self.set_belt_stopped_after_reset())

    def set_belt_stopped_after_reset(self):
        self.belt_status = "Stopped"
        self.update_status_bar()
        self.log("Reset complete - Belt stopped")

    def toggle_logs(self, value):
        if value:
            self.logs.grid()
        else:
            self.logs.grid_remove()

    def toggle_od(self, value):
        self.od_enabled = value
        state = "enabled" if value else "disabled"
        icon = "ON" if value else "OFF"
        self.log(f"[{icon}] Object Detection {state}")

    def toggle_class(self, value):
        self.class_enabled = value
        state = "enabled" if value else "disabled"
        icon = "ON" if value else "OFF"
        self.log(f"[{icon}] Classification {state}")

    def toggle_save_crops(self, value):
        self.save_crops_enabled = value
        icon = "ON" if value else "OFF"
        self.log(f"[{icon}] Save All Crops: {value}")

    def clear_logs(self):
        dirs_to_clear = [
            os.path.join("logs", "crops"),
            config.NON_ORANGE_LOG_DIR
        ]
        
        for d in dirs_to_clear:
            if os.path.exists(d):
                shutil.rmtree(d)
                os.makedirs(d, exist_ok=True)
        
        self.log("Logs cleared successfully")

    def update_gui(self):
        if not self.app_running:
            return
            
        if self.running:
            frame = self.video.read()
            if frame is None:
                pass
            else:
                if self.od_enabled:
                    results = self.tracker.track(frame)
                    
                    if results and results[0].boxes and results[0].boxes.id is not None:
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        ids = results[0].boxes.id.cpu().numpy().astype(int)
                        clss = results[0].boxes.cls.cpu().numpy().astype(int)
                        names = results[0].names
                        
                        for box, track_id, cls in zip(boxes, ids, clss):
                            x1, y1, x2, y2 = box.astype(int)
                            h, w = frame.shape[:2]
                            x1, y1 = max(0, x1), max(0, y1)
                            x2, y2 = min(w, x2), min(h, y2)
                            
                            crop = frame[y1:y2, x1:x2]
                            if crop.size == 0:
                                continue
                            
                            is_new = track_id not in self.aggregator.buffers
                            buf = self.aggregator.update(track_id, crop)
                            
                            if is_new:
                                class_name = names[cls]
                                buf.od_class_name = class_name
                            
                            if buf.od_class_name != "orange":
                                folder_name = f"{buf.od_class_name}_{track_id}"
                                folder_path = os.path.join(config.NON_ORANGE_LOG_DIR, folder_name)
                                os.makedirs(folder_path, exist_ok=True)
                                
                                timestamp = int(time.time() * 1000)
                                img_name = f"{timestamp}.jpg"
                                cv2.imwrite(os.path.join(folder_path, img_name), crop)

                            if self.save_crops_enabled:
                                folder_name = f"{buf.od_class_name}_{track_id}"
                                folder_path = os.path.join("logs", "crops", folder_name)
                                os.makedirs(folder_path, exist_ok=True)
                                
                                timestamp = int(time.time() * 1000)
                                img_name = f"{timestamp}.jpg"
                                cv2.imwrite(os.path.join(folder_path, img_name), crop)

                            if self.class_enabled and self.classifier.model:
                                preds = self.classifier.classify_batch([crop])
                                if preds:
                                    label_id, conf = preds[0]
                                    buf.update_classification(label_id)
                            
                            centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
                            prev_centroid = getattr(buf, 'last_centroid', None)
                            buf.last_centroid = centroid
                            
                            if self.line_counter.check_crossing(track_id, centroid, prev_centroid):
                                if buf.od_class_name == "orange":
                                    label = "rotten" if buf.classification_result == 1 else "fresh"
                                else:
                                    label = "non_orange"
                                self.line_counter.increment(label)
                                self.stats_panel.update_chart(self.line_counter.get_counts())

                    removed_buffers = self.aggregator.cleanup()
                    for buf in removed_buffers:
                        # Logic: 
                        # - If not orange -> 'R'
                        # - If orange and rotten -> 'R'
                        # - If orange and fresh -> 'F'
                        
                        serial_val = 'R'
                        log_label = "Non-orange/Rotten"
                        
                        if buf.od_class_name == "orange":
                            if not buf.is_rotten:
                                serial_val = 'F'
                                log_label = "Fresh"
                            else:
                                serial_val = 'R'
                                log_label = "Rotten"
                        else:
                            serial_val = 'R'
                            log_label = "Non-orange"
                        
                        # Send the character
                        self.serial.send_classification(serial_val)

                        self.log("-" * 40)
                        self.log(f"Object {buf.track_id} exited")
                        self.log(f"   Frames seen: {buf.total_frames}")
                        self.log(f"   Class: {buf.od_class_name}")
                        self.log(f"   Verdict: {log_label} -> Sending '{serial_val}'")

                    frame = draw_boxes(frame, results, self.aggregator.buffers)
                    frame = draw_counting_line(frame, self.line_counter)
                    frame = draw_info(frame, self.line_counter.get_counts())
                
                # Display with better scaling
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                
                # Scale image to fit label while maintaining aspect ratio
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()
                
                if label_width > 1 and label_height > 1:
                    img.thumbnail((label_width, label_height), Image.Resampling.LANCZOS)
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        
        if self.app_running:
            self.after_id = self.root.after(config.GUI_REFRESH_INTERVAL, self.update_gui)

    def on_close(self):
        self.app_running = False
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except:
                pass
            self.after_id = None
            
        self.stop_conveyor_belt()
        if self.serial:
            self.serial.close()
            
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass