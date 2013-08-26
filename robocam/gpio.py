try:
    import RPIO
except Exception:
    """Enbale testing on pc"""
import time


class DistanceTarget(object):
    """Distance target"""

    def __init__(self, options, distance):
        self.result = distance
        self.options = options
        self.pulse = 0.0001
        self.timeout = 2100
        self.countdown = self.timeout
        self._init_pins()
        self.loop()

    def _init_pins(self):
        """Init pins"""
        RPIO.setmode(RPIO.BCM)
        RPIO.setup(self.options.echo_pin, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
        RPIO.setup(self.options.trig_pin, RPIO.OUT)
        self.set_trig(False)
        time.sleep(2)

    def set_trig(self, value):
        """Set trig"""
        RPIO.output(self.options.trig_pin, value)

    def get_echo(self):
        """Read echo"""
        return RPIO.input(self.options.echo_pin)

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

    def loop(self):
        """Main loop"""
        while True:
            self.pulse_trig()
            duration = self.get_duration()
            if self.countdown > 0 and duration is not None:
                self.result.value = duration * 1000000 / 58

            time.sleep(0.1)
