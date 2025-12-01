import cv2
import threading
import time
import os

class VideoInput:
    """
    A threaded video input class to ensure the main processing loop isn't blocked by camera I/O.
    """
    def __init__(self, source=0, width=1280, height=720, fps=30):
        self.source = source
        self.width = width
        self.height = height
        self.target_fps = fps
        
        self.cap = cv2.VideoCapture(self.source)
        
        # Set resolution
        # Note: Some cameras might not support exact requested resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()
        self.stopped = False

        # Get the actual FPS of the video source
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0 or self.fps > 1000:
             # Fallback if FPS is not valid
            self.fps = self.target_fps
        
        self.frame_delay = 1.0 / self.fps

    def start(self):
        if self.started:
            return self
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        while not self.stopped:
            start_time = time.time()
            grabbed, frame = self.cap.read()
            
            if not grabbed:
                # If reading failed, it might be end of video file.
                # Check if it's a file (source is str) and loop
                if isinstance(self.source, str) and os.path.exists(self.source):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    # Camera disconnected or error
                    with self.read_lock:
                        self.grabbed = False
                    break

            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame
            
            # Control playback speed to match FPS
            elapsed = time.time() - start_time
            delay = self.frame_delay - elapsed
            if delay > 0:
                time.sleep(delay) 

    def read(self):
        with self.read_lock:
            if not self.grabbed:
                return None
            return self.frame.copy()

    def stop(self):
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join()
        self.cap.release()

    def is_opened(self):
        return self.cap.isOpened()
