from unittest import TestCase
from multiprocessing import Array
from mock import MagicMock
from robocam.arduino import GyroAccelTarget


class GyroAccelCase(TestCase):
    """Gyro and accel case"""

    def setUp(self):
        self._mock_serial()
        self.result = Array('i', 6)
        self.target = GyroAccelTarget()
        self.target._result = self.result

    def _mock_serial(self):
        """Mock connection to serial port"""
        self._orig_connection = GyroAccelTarget._init_connection
        GyroAccelTarget._init_connection = MagicMock()
        GyroAccelTarget._serial = MagicMock()

    def tearDown(self):
        GyroAccelTarget._init_connection = self._orig_connection
        del GyroAccelTarget._serial

    def test_read_values(self):
        """Test read values"""
        GyroAccelTarget._serial.readline.return_value = '1 2 3 4 5 6\n\r'
        vals = self.target.read_values()
        self.assertItemsEqual(vals, range(1, 7))

    def test_fails_on_read(self):
        """Test fails on read"""
        GyroAccelTarget._serial.readline.return_value = '1 2 3 4 5\n\r'
        with self.assertRaises(Exception):
            self.target.read_values()

    def test_share_values(self):
        """Test share values"""
        self.target.share_values(range(6))
        self.assertItemsEqual(list(self.result), range(6))
