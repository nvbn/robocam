from unittest import TestCase
from multiprocessing import Array
from mock import MagicMock
from robocam.arduino import GyroAccel


class GyroAccelCase(TestCase):
    """Gyro and accel case"""

    def setUp(self):
        self._mock_serial()
        self.result = Array('i', 6)
        self.target = GyroAccel()
        self.target._redis = MagicMock()

    def _mock_serial(self):
        """Mock connection to serial port"""
        self._orig_connection = GyroAccel._init_connection
        GyroAccel._init_connection = MagicMock()
        GyroAccel._serial = MagicMock()

    def tearDown(self):
        GyroAccel._init_connection = self._orig_connection
        del GyroAccel._serial

    def test_read_values(self):
        """Test read values"""
        GyroAccel._serial.readline.return_value = '1 2 3 4 5 6\n\r'
        vals = self.target.read_values()
        self.assertItemsEqual(vals, range(1, 7))

    def test_fails_on_read(self):
        """Test fails on read"""
        GyroAccel._serial.readline.return_value = '1 2 3 4 5\n\r'
        with self.assertRaises(Exception):
            self.target.read_values()

    def test_share_values(self):
        """Test share values"""
        values = range(6)
        self.target.share_values(values)
        self.target._redis._publish.assert_called_once()
