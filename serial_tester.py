import customtkinter as ctk
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from config import config
from hardware.serial_comm import SerialCommunicator

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SerialTester(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Serial Tester")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.serial = SerialCommunicator(port=config.SERIAL_PORT, baud_rate=config.BAUD_RATE)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(self, text="Hardware Tester", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Connection Status
        self.status_label = ctk.CTkLabel(self, text=f"Port: {config.SERIAL_PORT} | Status: Disconnected",
                                         text_color="red")
        self.status_label.pack(pady=(0, 20))
        
        if self.serial.connected:
            self.status_label.configure(text=f"Port: {config.SERIAL_PORT} | Status: Connected",
                                      text_color="green")
            
        # Commands Frame
        cmd_frame = ctk.CTkFrame(self)
        cmd_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(cmd_frame, text="Control Commands").pack(pady=5)
        
        btn_start = ctk.CTkButton(cmd_frame, text="SEND 'START'", command=lambda: self.send_cmd("START"),
                                 fg_color="green", hover_color="#006400")
        btn_start.pack(pady=5, padx=20, fill="x")
        
        btn_stop = ctk.CTkButton(cmd_frame, text="SEND 'STOP'", command=lambda: self.send_cmd("STOP"),
                                fg_color="red", hover_color="#8B0000")
        btn_stop.pack(pady=5, padx=20, fill="x")
        
        btn_reset = ctk.CTkButton(cmd_frame, text="SEND 'RESET'", command=lambda: self.send_cmd("RESET"),
                                 fg_color="orange", hover_color="#CD8500")
        btn_reset.pack(pady=5, padx=20, fill="x")

        # Classification Frame
        cls_frame = ctk.CTkFrame(self)
        cls_frame.pack(padx=20, pady=20, fill="x")
        
        ctk.CTkLabel(cls_frame, text="Classification Signals").pack(pady=5)
        
        grid_frame = ctk.CTkFrame(cls_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=5)
        
        btn_f = ctk.CTkButton(grid_frame, text="SEND 'F' (Fresh)", command=lambda: self.send_signal("F"))
        btn_f.pack(side="left", expand=True, padx=5)
        
        btn_r = ctk.CTkButton(grid_frame, text="SEND 'R' (Rotten)", command=lambda: self.send_signal("R"),
                             fg_color="#8B0000", hover_color="#500000")
        btn_r.pack(side="right", expand=True, padx=5)

        # Log
        self.log_box = ctk.CTkTextbox(self, height=100)
        self.log_box.pack(padx=20, pady=10, fill="x")
        self.log("Ready to test...")

    def send_cmd(self, cmd):
        if self.serial.connected:
            self.serial.send_command(cmd)
            self.log(f"Sent Command: {cmd}")
        else:
            self.log("Error: Not Connected")
            self.reconnect()

    def send_signal(self, signal):
        if self.serial.connected:
            self.serial.send_classification(signal)
            self.log(f"Sent Signal: {signal}")
        else:
            self.log("Error: Not Connected")
            self.reconnect()

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert("0.0", f"[{timestamp}] {msg}\n")

    def reconnect(self):
        self.log("Attempting to reconnect...")
        self.serial.connect()
        if self.serial.connected:
            self.status_label.configure(text=f"Port: {config.SERIAL_PORT} | Status: Connected",
                                      text_color="green")
            self.log("Reconnected!")
        else:
            self.status_label.configure(text=f"Port: {config.SERIAL_PORT} | Status: Disconnected",
                                      text_color="red")
            self.log("Connection Failed.")

if __name__ == "__main__":
    app = SerialTester()
    app.mainloop()
