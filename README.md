# Orange Detection System

A real-time Python system that detects, tracks, counts, and classifies oranges on a conveyor using YOLOv8n. The system includes a Tkinter GUI, a thread-safe Queue for hardware integration, and a modular architecture.

## Features
- **Detection & Tracking**: Uses `yolov8n.pt` and BoT-SORT/ByteTrack.
- **Classification**: Classifies oranges as "Fresh" or "Rotten" using `best.pt`.
- **Counting**: Configurable line counting (horizontal/vertical).
- **Hardware Integration**: Thread-safe queue with a sensor reader interface (simulation mode included).
- **GUI**: Live video feed, overlays, counters, queue view, and controls.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Models**:
   - Ensure `models/yolov8n.pt` exists (will be downloaded automatically by Ultralytics if missing).
   - Ensure `models/best.pt` exists for classification. **Note**: You need to provide your trained classifier model at this path.

3. **Configuration**:
   - Edit `config/config.py` to adjust settings like `CAMERA_ID`, `LINE_POSITION`, `SIMULATE_SENSOR`, etc.

## Running the System

To start the application:
```bash
python main.py
```

## Usage

- **Start/Stop**: Use the buttons in the GUI to start or stop the video processing.
- **Line Position**: Adjust the slider to move the counting line.
- **Simulation**: If `SIMULATE_SENSOR` is True in config, the system will automatically pop items from the queue every few seconds.
- **Manual Pop**: Click "Manual Pop Queue" to simulate a hardware trigger.
- **Export**: Click "Export Queue" to save the current queue data to a CSV file.

## Project Structure
- `main.py`: Entry point.
- `config/`: Configuration file.
- `detector/`: YOLOv8 wrappers for detection, tracking, and classification.
- `processing/`: Logic for buffering, counting, and queue management.
- `gui/`: Tkinter application and widgets.
- `utils/`: Helper functions for video, drawing, and storage.
- `hardware/`: Sensor interface.
