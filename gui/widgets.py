import tkinter as tk
from tkinter import ttk
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class QueueVisualizer(ttk.LabelFrame):
    """
    Widget to display the queue horizontally: start 1, 0, 1, ... end
    """
    def __init__(self, parent):
        super().__init__(parent, text="Queue State")
        self.lbl_content = ttk.Label(self, text="start -> end", font=("Consolas", 12))
        self.lbl_content.pack(fill=tk.X, expand=True, padx=5, pady=10)
        
    def update_list(self, items):
        display_str = "start "
        values = []
        for item in items:
            label = item.get('label')
            # Map label to 0/1. 
            val = "1" if label == "rotten" else "0" 
            values.append(val)
            
        display_str += ", ".join(values)
        display_str += " end"
        self.lbl_content.config(text=display_str)

class LogPanel(ttk.LabelFrame):
    """
    Widget to display logs.
    """
    def __init__(self, parent):
        super().__init__(parent, text="System Logs")
        self.text_area = tk.Text(self, height=10, state='disabled')
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def log(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

class ControlPanel(ttk.LabelFrame):
    """
    Widget for user controls.
    """
    def __init__(self, parent, callbacks):
        super().__init__(parent, text="Controls")
        self.callbacks = callbacks
        
        # Toggle OD Model
        self.var_od = tk.BooleanVar(value=True)
        self.chk_od = ttk.Checkbutton(self, text="Object Detection", 
                                      variable=self.var_od,
                                      command=lambda: self.callbacks['toggle_od'](self.var_od.get()))
        self.chk_od.pack(fill=tk.X, padx=5, pady=2)
        
        # Toggle Classification Model
        self.var_class = tk.BooleanVar(value=True)
        self.chk_class = ttk.Checkbutton(self, text="Classification", 
                                         variable=self.var_class,
                                         command=lambda: self.callbacks['toggle_class'](self.var_class.get()))
        self.chk_class.pack(fill=tk.X, padx=5, pady=2)
        
        # Manual Pop
        self.btn_pop = ttk.Button(self, text="Pop from Queue", command=self.callbacks['manual_pop'])
        self.btn_pop.pack(fill=tk.X, padx=5, pady=2)
        
        # Clear Queue
        self.btn_clear = ttk.Button(self, text="Clear Queue", command=self.callbacks['clear_queue'])
        self.btn_clear.pack(fill=tk.X, padx=5, pady=2)

        # Clear Logs
        self.btn_clear_logs = ttk.Button(self, text="Clear Logs", command=self.callbacks['clear_logs'])
        self.btn_clear_logs.pack(fill=tk.X, padx=5, pady=2)

        # Save Crops Checkbox
        self.var_save_crops = tk.BooleanVar(value=False)
        self.chk_save_crops = ttk.Checkbutton(self, text="Save All Crops", 
                                              variable=self.var_save_crops,
                                              command=lambda: self.callbacks['toggle_save_crops'](self.var_save_crops.get()))
        self.chk_save_crops.pack(fill=tk.X, padx=5, pady=2)
