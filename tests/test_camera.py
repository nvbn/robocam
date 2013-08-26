from multiprocessing import Queue
from unittest import TestCase
from mock import MagicMock
from robocam import camera


class BaseCameraCase(TestCase):
    """Base camera case"""

    def setUp(self):
        self.camera = camera.Camera('')
        self.camera.run = MagicMock()
        self.camera._proc = MagicMock()


class CameraCase(BaseCameraCase):
    """Camera case"""

    def test_stop(self):
        """Test stop"""
        self.camera.stop()
        self.camera._proc.kill.assert_called_once_with()

    def test_is_run(self):
        """Test is run"""
        self.camera._proc.poll.return_value = None
        self.assertTrue(self.camera.is_run())

    def test_isnt_run(self):
        """Test isnt run"""
        self.camera._proc.poll.return_value = 0
        self.assertFalse(self.camera.is_run())


class CameraTargetCase(BaseCameraCase):
    """Camera target case"""

    def setUp(self):
        super(CameraTargetCase, self).setUp()
        self.camera.is_run = MagicMock()
        self.queue = Queue()
        self.target = camera.CameraTarget()
        self.target._camera = self.camera
        self.target._queue = self.queue

    def test_has_changes_form_queue(self):
        """Test has changes from queue"""
        self.queue.put('test')
        self.camera.is_run.return_value = True
        self.assertTrue(self.target.has_changes())

    def test_has_changes_form_camera(self):
        """Test has changes from camera"""
        self.camera.is_run.return_value = False
        self.assertTrue(self.target.has_changes())

    def test_has_no_changes(self):
        """Test has no changes"""
        self.camera.is_run.return_value = True
        self.assertFalse(self.target.has_changes())
