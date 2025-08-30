import pytest
from src.gyro_reader.gyro import GyroReader

def test_init():
    gyro = GyroReader()
    assert gyro.get_compass() == 0
    assert gyro.get_tilt() == 0