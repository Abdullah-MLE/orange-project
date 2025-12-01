import sys
import os
import time
import threading

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processing.queue_manager import QueueManager
from hardware.sensor_reader import SensorReader
from config import config

def test_queue_hardware():
    print("Testing Queue and Hardware...")
    
    # 1. Test Queue
    qm = QueueManager()
    qm.push({"id": 1, "label": "fresh"})
    qm.push({"id": 2, "label": "rotten"})
    
    assert qm.size() == 2
    print("Queue size check passed.")
    
    item = qm.pop()
    assert item["id"] == 1
    print("Queue pop check passed.")
    
    # 2. Test Sensor Reader (Simulation)
    # Set simulation interval to fast for testing
    config.SIMULATION_INTERVAL = 0.5
    config.SIMULATE_SENSOR = True
    
    sr = SensorReader(qm)
    sr.start()
    
    # Push some items
    qm.push({"id": 3, "label": "fresh"})
    qm.push({"id": 4, "label": "rotten"})
    
    print("Waiting for sensor to pop items...")
    time.sleep(2.0) # Should pop at least 2 items (0.5s interval)
    
    sr.stop()
    
    # Check if items were popped (queue should be empty or smaller)
    # We pushed 2 items (plus 1 remaining from before = id 2). Total 3.
    # In 2.0s, it should pop ~4 times. So queue should be empty.
    
    current_size = qm.size()
    print(f"Final queue size: {current_size}")
    
    if current_size == 0:
        print("Sensor reader verification passed.")
    else:
        print(f"Sensor reader verification warning: Queue not empty (size {current_size}).")

if __name__ == "__main__":
    test_queue_hardware()
