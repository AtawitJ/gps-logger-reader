import serial.tools.list_ports
from serial import Serial, SerialException
import math
import threading
import time
import logging

class GyroReader:
    def __init__(self, alpha=0.5, beta=0.7):
        self.sp = None
        self.nmea = None
        self.lock = threading.Lock()
        self.stop_thread = False
        self.compass = 0
        self.tilt = 0
        self.alpha = alpha
        self.beta = beta
        self.tilt_values = []

    def start(self):
        if not hasattr(self, 'thread'):
            self.thread = threading.Thread(target=self.read)
        self.thread.start()

    def connect(self):
        while not self.stop_thread:
            self.ports = list(serial.tools.list_ports.comports())
            if not self.ports:
                print("Gyroscope device not found.")
                return None
            for port in self.ports:
                try:
                    if port.manufacturer == "Aaronia AG":
                        print(f"Gyroscope connecting to port {port.device}")
                        self.sp = Serial(port.device, baudrate=625000, stopbits=2, parity='N')
                        self.sp.write(b"$PAAG,ID\r\n")
                        self.sp.write(b"$PAAG,MODE,START,RATE,30\r\n")
                        print("Gyroscope connected successfully!")
                        return self.sp
                except SerialException:
                    pass
            time.sleep(2)

    def read(self):
        previous_compass = 0
        previous_tilt = 0
        time.sleep(2)
        while not self.stop_thread:
            with self.lock:
                if not self.sp:
                    self.connect()
                    time.sleep(2)
                    continue
                try:
                    self.nmea = self.sp.readline().strip().decode().split(',')
                    if len(self.nmea) >= 3:
                        if str(self.nmea[0]) == "$PAAG" and str(self.nmea[1]) == "DATA":
                            if str(self.nmea[2]) == "C":
                                try:
                                    heading_rad = math.atan2(float(self.nmea[5]), float(self.nmea[4]))
                                    heading_deg = (heading_rad + math.pi) * 180 / math.pi
                                    raw_compass = float("%.1f" % heading_deg)
                                    self.compass = (1 - self.alpha) * raw_compass + self.alpha * previous_compass
                                    previous_compass = self.compass
                                except (IndexError, ValueError) as e:
                                    logging.error(f"Error calculating compass: {e}")
                            elif str(self.nmea[2]) == "T":
                                try:
                                    x = float(self.nmea[4]) / 8192
                                    y = float(self.nmea[5]) / 8192
                                    z = float(self.nmea[6]) / 8192
                                    raw_tilt = math.degrees(-math.atan2(y, math.sqrt((x*x)+(z*z))))
                                    raw_tilt = float("%.1f" % raw_tilt)
                                    self.tilt = (1 - self.beta) * raw_tilt + self.beta * previous_tilt
                                    previous_tilt = self.tilt
                                    self.tilt_values.append(self.tilt)
                                    self.average_tilt = sum(self.tilt_values[-20:]) / min(len(self.tilt_values), 20)
                                except (IndexError, ValueError) as e:
                                    logging.error(f"Error calculating tilt: {e}")
                except SerialException as e:
                    logging.error(f"Error reading from serial port: {e}")
                    self.sp = None

    def get_compass(self):
        return self.compass

    def get_tilt(self):
        if hasattr(self, 'average_tilt') and self.average_tilt:
            return self.average_tilt
        else:
            return 0

    def close(self):
        self.stop_thread = True
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join()
        if self.sp and self.sp.is_open:
            self.sp.close()
        print("GyroReader Module Closed.")
