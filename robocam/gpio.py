try:
    import RPIO
except Exception:
    """Enbale testing on pc"""
import time
import json
import redis
from . import const


class Distance(object):
    """Distance target"""

    def __init__(self):
        self._redis = redis.Redis()
        self.pulse = 0.0001
        self.timeout = 2100
        self.countdown = self.timeout
        self._init_pins()

    def _init_pins(self):
        """Init pins"""
        RPIO.setmode(RPIO.BCM)
        RPIO.setup(const.ECHO_PIN, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.setup(const.TRIG_PIN, RPIO.OUT)
        self.set_trig(False)
        time.sleep(2)

    def set_trig(self, value):
        """Set trig"""
        RPIO.output(const.TRIG_PIN, value)

    def get_echo(self):
        """Read echo"""
        return RPIO.input(const.ECHO_PIN)

    def wait_echo(self, value):
        """Wait echo"""
        while self.get_echo() == value and self.countdown > 0:
            self.countdown -= 1

    def pulse_trig(self):
        """Pulse trig"""
        self.set_trig(True)
        time.sleep(self.pulse)
        self.set_trig(False)
        self.countdown = self.timeout
        self.wait_echo(0)

    def get_duration(self):
        """Get duration"""
        if self.countdown > 0:
            start = time.time()
            self.countdown = self.timeout
            self.wait_echo(1)
            end = time.time()
            return end - start
        else:
            return None

    def run(self):
        """Main loop"""
        while True:
            self.pulse_trig()
            duration = self.get_duration()
            if self.countdown > 0 and duration is not None:
                value = duration * 1000000 / 58
                self._redis.publish(const.REDIS_CHANNEL, json.dumps(value))

            time.sleep(0.1)


def main():
    distance = Distance()
    distance.run()
