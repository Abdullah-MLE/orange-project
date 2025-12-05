import serial
import time
import threading

class SerialCommunicator:
    def __init__(self, port, baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.connected = False
        
        self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2) # Wait for connection to stabilize
            self.connected = True
            print(f"Connected to Serial Device on {self.port}")
        except Exception as e:
            print(f"Failed to connect to serial: {e}")
            self.connected = False

    def send_command(self, command):
        """
        Send a text command like 'start' or 'stop'.
        """
        if self.connected and self.ser:
            try:
                msg = f"{command}\n".encode('utf-8')
                self.ser.write(msg)
                print(f"Serial Sent: {command}")
            except Exception as e:
                print(f"Serial Error sending {command}: {e}")
                self.connected = False # Assume disconnected on error

    def send_classification(self, value):
        """
        Send a classification value (0 or 1).
        """
        if self.connected and self.ser:
            try:
                # Ensure value is integer 0 or 1
                val_to_send = str(int(value)).encode('utf-8')
                self.ser.write(val_to_send)
                print(f"Serial Sent Value: {value}")
            except Exception as e:
                print(f"Serial Error sending value {value}: {e}")
                self.connected = False

    def close(self):
        if self.ser:
            self.ser.close()
            self.connected = False
