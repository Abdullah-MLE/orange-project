import customtkinter as ctk
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.app import App
from config import config

def main():
    print("Initializing Orange Detection System...")
    
    # Initialize GUI
    root = ctk.CTk()
    app = App(root)
    
    # Start GUI Loop
    print("Starting GUI...")
    root.mainloop()

if __name__ == "__main__":
    main()
