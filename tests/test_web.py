from multiprocessing import Queue, Value
from uuid import uuid4
import os
from tornado.testing import AsyncHTTPTestCase
from robocam import web


class BaseWebCaseMixin(object):
    """Base case for robocam.web"""

    def setUp(self):
        super(BaseWebCaseMixin, self).setUp()
        self._create_app()

    def _mock_fifo(self):
        """Mock fifo"""
        self._orig_fifo = web.FIFO_PATH
        web.FIFO_PATH = os.path.join('/tmp', 'fifo{}'.format(uuid4().hex))
        with open(web.FIFO_PATH, 'w') as fl:
            fl.write('')

    def _create_app(self):
        if not hasattr(self, '_app'):
            self._mock_fifo()
            self.camera_queue = Queue()
            self.arm_queue = Queue()
            self.distance = Value('f', 0)
            self._app = web.WebApp(self.camera_queue, self.arm_queue, self.distance)

    def tearDown(self):
        super(BaseWebCaseMixin, self).tearDown()
        os.unlink(web.FIFO_PATH)
        web.FIFO_PATH = self._orig_fifo

    @property
    def app(self):
        self._create_app()
        return self._app

    def get_app(self):
        return self.app


class IndexHandlerCase(BaseWebCaseMixin, AsyncHTTPTestCase):
    """Check index handler"""

    def test_get(self):
        """Test get"""
        response = self.fetch('/')
        self.assertEqual(response.code, 200)


class CameraHandlerCase(BaseWebCaseMixin, AsyncHTTPTestCase):
    """Camera handler case"""

    def test_get_image(self):
        """Test get image"""
        with open(web.FIFO_PATH, 'w') as fl:
            fl.write('test')
        response = self.fetch('/camera/')
        self.assertEqual(response.body, 'test')

    def test_post_params(self):
        """Test post params"""
        self.fetch('/camera/', method='POST', body='attrs=test')
        self.assertEqual(self.camera_queue.get(), 'test')


class ArmHandlerCase(BaseWebCaseMixin, AsyncHTTPTestCase):
    """Arm handler case"""

    def test_post_action(self):
        """Test post action"""
        self.fetch('/arm/', method='POST', body='part=base&action=test')
        self.assertEqual(self.arm_queue.get(), ('base', 'test'))
