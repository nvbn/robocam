import serial
import json
import redis
from . import const


class GyroAccel(object):
    """Gyro and accel"""

    def __init__(self):
        self._init_connection()
        self._redis = redis.Redis()

    def _init_connection(self):
        self._serial = serial.Serial(
            const.ARDUINO_TTY, const.ARDUINO_BAUDRATE
        )

    def read_values(self):
        """Read values from port"""
        line = self._serial.readline()
        vals = map(int, line[:-2].split(' '))
        if len(vals) != 6:
            raise Exception()
        return vals

    def share_values(self, values):
        """Share values"""
        result = json.dumps(['gyro'] + values)
        self._redis.publish(const.REDIS_CHANNEL, result)

    def run(self):
        """Consuming loop"""
        while True:
            try:
                values = self.read_values()
                self.share_values(values)
            except Exception as e:
                print e


def main():
    gyroaccel = GyroAccel()
    gyroaccel.run()
