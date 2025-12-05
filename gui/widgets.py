import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import config

class LogPanel(ctk.CTkFrame):
    """Enhanced log panel with scrollbar"""
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10, fg_color=("#242424", "#1a1a1a"))
        
        # Header
        header = ctk.CTkFrame(self, height=45, corner_radius=0, 
                             fg_color=("#2b2b2b", "#1f1f1f"))
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="System Logs", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(side="left", padx=15, pady=10)
        
        # Clear button in header
        self.clear_btn = ctk.CTkButton(header, text="Clear", width=70, height=28,
                                      corner_radius=6, fg_color="#ef4444",
                                      hover_color="#dc2626",
                                      command=self.clear_logs)
        self.clear_btn.pack(side="right", padx=15, pady=10)
        
        # Text area with scrollbar in consistent color
        text_container = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#0f0f0f"))
        text_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create scrollable textbox
        self.text_area = ctk.CTkTextbox(text_container, 
                                       font=ctk.CTkFont(family="Consolas", size=11),
                                       fg_color=("#1a1a1a", "#0f0f0f"),
                                       border_width=0,
                                       corner_radius=0,
                                       wrap="word",
                                       scrollbar_button_color=("#404040", "#2a2a2a"),
                                       scrollbar_button_hover_color=("#505050", "#3a3a3a"))
        self.text_area.pack(fill="both", expand=True, padx=8, pady=8)
        
    def log(self, message):
        self.text_area.insert("end", message + "\n")
        self.text_area.see("end")
        
    def clear_logs(self):
        self.text_area.delete("1.0", "end")

class StatsPanel(ctk.CTkFrame):
    """Enhanced statistics panel with beautiful chart"""
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10, fg_color=("#242424", "#1a1a1a"))
        
        # Header
        header = ctk.CTkFrame(self, height=45, corner_radius=0,
                             fg_color=("#2b2b2b", "#1f1f1f"))
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="Live Statistics", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(side="left", padx=15, pady=10)
        
        # Chart container
        chart_container = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#0f0f0f"))
        chart_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(5, 3.5), dpi=100, facecolor='#1a1a1a')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a1a1a')
        
        self.categories = ['Fresh', 'Rotten', 'Non-Orange']
        self.colors = ['#4ade80', '#ef4444', '#fbbf24']
        
        # Initial data
        self.counts = [0, 0, 0]
        self.bars = self.ax.bar(self.categories, self.counts, color=self.colors, 
                               width=0.6, edgecolor='white', linewidth=1.5)
        
        # Styling
        self.ax.set_ylim(0, 10)
        self.ax.set_ylabel('Count', fontsize=11, fontweight='bold', color='white')
        self.ax.tick_params(colors='white', labelsize=10)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#404040')
        self.ax.spines['bottom'].set_color('#404040')
        self.ax.grid(axis='y', alpha=0.2, linestyle='--', color='gray')
        
        # Add value labels on bars
        self.value_labels = []
        for bar in self.bars:
            label = self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                               '0', ha='center', va='bottom', 
                               fontweight='bold', fontsize=10, color='white')
            self.value_labels.append(label)
        
        self.fig.tight_layout()
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        
    def update_chart(self, counts_dict):
        fresh = counts_dict.get('fresh', 0)
        rotten = counts_dict.get('rotten', 0)
        non_orange = counts_dict.get('non_orange', 0)
        
        new_counts = [fresh, rotten, non_orange]
        
        # Update bar heights and labels
        for bar, count, label in zip(self.bars, new_counts, self.value_labels):
            bar.set_height(count)
            label.set_text(str(count))
            label.set_y(count)
            
        # Adjust Y-axis
        max_count = max(new_counts) if new_counts else 0
        self.ax.set_ylim(0, max(10, max_count + 5))
        
        self.canvas.draw()

class ControlPanel(ctk.CTkFrame):
    """Enhanced control panel with horizontal buttons and grouped switches"""
    def __init__(self, parent, callbacks):
        super().__init__(parent, corner_radius=10, fg_color=("#242424", "#1a1a1a"))
        self.callbacks = callbacks
        
        # Header
        header = ctk.CTkFrame(self, height=45, corner_radius=0,
                             fg_color=("#2b2b2b", "#1f1f1f"))
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="Control Panel", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(side="left", padx=15, pady=10)
        
        # Controls container with consistent color
        controls_container = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#0f0f0f"))
        controls_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        inner_container = ctk.CTkFrame(controls_container, fg_color="transparent")
        inner_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # === MAIN CONTROL BUTTONS (HORIZONTAL) ===
        buttons_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 15))
        
        # Configure grid for 3 columns
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        
        # Start Button
        self.btn_start = ctk.CTkButton(
            buttons_frame, 
            text="START",
            command=self.callbacks['start_camera'],
            fg_color="#22c55e",
            hover_color="#16a34a",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=70,
            corner_radius=10
        )
        self.btn_start.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Stop Button
        self.btn_stop = ctk.CTkButton(
            buttons_frame,
            text="STOP",
            command=self.callbacks['stop_camera'],
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=70,
            corner_radius=10
        )
        self.btn_stop.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Reset Button
        self.btn_reset = ctk.CTkButton(
            buttons_frame,
            text="RESET",
            command=self.callbacks['reset_hardware'],
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=70,
            corner_radius=10
        )
        self.btn_reset.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        # === SEPARATOR ===
        separator = ctk.CTkFrame(inner_container, height=2, 
                                fg_color=("#404040", "#2a2a2a"))
        separator.pack(fill="x", pady=15)
        
        # === MODEL TOGGLES SECTION (2x2 Grid) ===
        model_label = ctk.CTkLabel(inner_container, text="Models", 
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   anchor="w")
        model_label.pack(fill="x", pady=(0, 10))
        
        model_toggles_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        model_toggles_frame.pack(fill="x", pady=(0, 15))
        
        # Configure 2x2 grid
        model_toggles_frame.grid_columnconfigure(0, weight=1)
        model_toggles_frame.grid_columnconfigure(1, weight=1)
        
        # Object Detection (Row 0, Col 0)
        self.var_od = ctk.BooleanVar(value=True)
        self.switch_od = ctk.CTkSwitch(
            model_toggles_frame,
            text="Detection",
            variable=self.var_od,
            command=lambda: self.callbacks['toggle_od'](self.var_od.get()),
            font=ctk.CTkFont(size=12),
            progress_color="#22c55e"
        )
        self.switch_od.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        # Classification (Row 0, Col 1)
        self.var_class = ctk.BooleanVar(value=True)
        self.switch_class = ctk.CTkSwitch(
            model_toggles_frame,
            text="Classify",
            variable=self.var_class,
            command=lambda: self.callbacks['toggle_class'](self.var_class.get()),
            font=ctk.CTkFont(size=12),
            progress_color="#a855f7"
        )
        self.switch_class.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="w")
        
        # === SEPARATOR ===
        separator2 = ctk.CTkFrame(inner_container, height=2,
                                 fg_color=("#404040", "#2a2a2a"))
        separator2.pack(fill="x", pady=15)
        
        # === OTHER TOGGLES SECTION (2x2 Grid) ===
        other_label = ctk.CTkLabel(inner_container, text="Options", 
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   anchor="w")
        other_label.pack(fill="x", pady=(0, 10))
        
        other_toggles_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        other_toggles_frame.pack(fill="x", pady=(0, 15))
        
        # Configure 2x2 grid
        other_toggles_frame.grid_columnconfigure(0, weight=1)
        other_toggles_frame.grid_columnconfigure(1, weight=1)
        
        # Show Logs (Row 0, Col 0)
        self.var_logs = ctk.BooleanVar(value=True)
        self.switch_logs = ctk.CTkSwitch(
            other_toggles_frame,
            text="Logs",
            variable=self.var_logs,
            command=lambda: self.callbacks['toggle_logs'](self.var_logs.get()),
            font=ctk.CTkFont(size=12),
            progress_color="#3b82f6"
        )
        self.switch_logs.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        # Save Crops (Row 0, Col 1)
        self.var_save_crops = ctk.BooleanVar(value=False)
        self.switch_save = ctk.CTkSwitch(
            other_toggles_frame,
            text="Crops",
            variable=self.var_save_crops,
            command=lambda: self.callbacks['toggle_save_crops'](self.var_save_crops.get()),
            font=ctk.CTkFont(size=12),
            progress_color="#f59e0b"
        )
        self.switch_save.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="w")
        
        # === SEPARATOR ===
        separator3 = ctk.CTkFrame(inner_container, height=2,
                                 fg_color=("#404040", "#2a2a2a"))
        separator3.pack(fill="x", pady=15)
        
        # === UTILITY BUTTON ===
        self.btn_clear = ctk.CTkButton(
            inner_container,
            text="Clear Logs",
            command=self.callbacks['clear_logs'],
            fg_color=("#404040", "#2a2a2a"),
            hover_color=("#505050", "#3a3a3a"),
            font=ctk.CTkFont(size=13),
            height=40,
            corner_radius=8
        )
        self.btn_clear.pack(fill="x")