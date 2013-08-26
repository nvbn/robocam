from unittest import TestCase
import os
from mock import MagicMock
from robocam import app
from robocam.const import FIFO_PATH


class AppCase(TestCase):
    """Robocam app case"""

    def setUp(self):
        self._orig_process = app.Process()
        app.Process = MagicMock()
        self.app = app.Robocam()
        self.app.run()

    def tearDown(self):
        app.Process = self._orig_process

    def test_fifo(self):
        """Test fifo exists"""
        self.assertTrue(os.path.exists(FIFO_PATH))
