import tkinter as tk
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.app import App
from processing.queue_manager import QueueManager
from config import config

def main():
    print("Initializing Orange Detection System...")
    
    # Initialize Queue
    queue_manager = QueueManager(max_size=config.QUEUE_MAX_SIZE)
    
    # Initialize GUI
    root = tk.Tk()
    app = App(root, queue_manager)
    
    # Start GUI Loop
    print("Starting GUI...")
    root.mainloop()

if __name__ == "__main__":
    main()
