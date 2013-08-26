import os
import json
import tornado.web
import tornado.ioloop
import tornado.template
from .const import FIFO_PATH


class IndexHandler(tornado.web.RequestHandler):
    """Index page handler"""

    def get(self, *args, **kwargs):
        self.render('index.html')


class CameraHandler(tornado.web.RequestHandler):
    """Camera image handler"""

    def __init__(self, application, *args, **kwargs):
        self._queue = application.camera_queue
        super(CameraHandler, self).__init__(application, *args, **kwargs)

    def get(self, *args, **kwargs):
        self.set_header('Content-type', 'image/jpeg')
        with open(FIFO_PATH) as img:
            self.write(img.read())

    def post(self, *args, **kwargs):
        self._queue.put(self.get_argument('attrs'))


class ArmHandler(tornado.web.RequestHandler):
    """Arm handler"""

    def __init__(self, application, *args, **kwargs):
        self._queue = application.arm_queue
        super(ArmHandler, self).__init__(application, *args, **kwargs)

    def post(self, *args, **kwargs):
        self._queue.put((
            self.get_argument('part'),
            self.get_argument('action'),
        ))


class DistanceHandler(tornado.web.RequestHandler):
    """Distance handler"""

    def __init__(self, application, *args, **kwargs):
        self._distance = application.distance
        super(DistanceHandler, self).__init__(application, *args, **kwargs)

    def get(self, *args, **kwargs):
        self.write(str(self._distance.value))


class GyroAccellHandler(tornado.web.RequestHandler):
    """Gyro and accell handler"""

    def __init__(self, application, *args, **kwargs):
        self._result_array = application.gyro_array
        super(GyroAccellHandler, self).__init__(application, *args, **kwargs)

    def get(self, *args, **kwargs):
        self.write(json.dumps(list(self._result_array)))


class WebApp(tornado.web.Application):
    """Web app"""

    def __init__(
            self, camera_queue, arm_queue, distance, gyro_array, **kwargs
    ):
        path = os.path.abspath(os.path.dirname(__file__))

        self.camera_queue = camera_queue
        self.arm_queue = arm_queue
        self.distance = distance
        self.gyro_array = gyro_array

        super(WebApp, self).__init__(
            [
                (r'/', IndexHandler),
                (r'/camera/', CameraHandler),
                (r'/arm/', ArmHandler),
                (r'/distance/', DistanceHandler),
                (r'/gyro/', GyroAccellHandler),
            ],
            template_path=os.path.join(path, '../templates'),
            static_path=os.path.join(path, '../static'),
            **kwargs
        )


def web_target(options, camera_queue, arm_queue, distance, gyro_array):
    """Web target"""
    app = WebApp(
        camera_queue, arm_queue, distance, gyro_array,
        debug=options.debug,
    )
    app.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()
