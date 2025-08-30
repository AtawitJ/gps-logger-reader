from gps_logger_reader import GyroReader

gyro = GyroReader()
gyro.start()
import time
for _ in range(10):
    print('Compass:', gyro.get_compass(), 'Tilt:', gyro.get_tilt())
    time.sleep(1)
gyro.close()
