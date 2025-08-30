# gps-logger-reader

A Python module for reading and processing GPS / Gyroscope logger data via serial connection.  
Includes filtering (low-pass) for compass and tilt values.

---

## Features
- Auto-detect serial port of GPS/Gyro device
- Reads NMEA `$PAAG` data frames
- Low-pass filter applied to compass and tilt values
- Thread-safe reader with start/stop
- Average tilt smoothing
- Example usage provided

---

## Installation
```bash
git clone https://github.com/your-username/gps-logger-reader.git
cd gps-logger-reader
pip install -e .
