import serial


class GyroAccelTarget(object):
    """Gyro and accel"""

    def __call__(self, options, result):
        self._result = result
        self._options = options
        self._init_connection()
        self.loop()

    def _init_connection(self):
        """init serial connection"""
        self._serial = serial.Serial(
            self._options.tty, self._options.baudrate,
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
        for num, val in enumerate(values):
            self._result[num] = val

    def loop(self):
        """Consuming loop"""
        while True:
            try:
                values = self.read_values()
                self.share_values(values)
            except Exception as e:
                print e


gyro_accel_target = GyroAccelTarget()
