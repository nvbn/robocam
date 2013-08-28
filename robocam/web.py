import os
import json
import tornado.web
import tornado.ioloop
import tornado.template
import tornado.websocket
import tornado.gen
import tornadoredis
from .const import DEBUG, REDIS_CHANNEL, PORT, HOST, REDIS_ARM_CHANNEL


class IndexHandler(tornado.web.RequestHandler):
    """Index page handler"""

    def get(self, *args, **kwargs):
        self.render('index.html')


class ArmHandler(tornado.web.RequestHandler):
    """Arm handler"""

    def __init__(self, application, *args, **kwargs):
        self.client = application.client
        super(ArmHandler, self).__init__(application, *args, **kwargs)

    def post(self, *args, **kwargs):
        self.client.publish(REDIS_ARM_CHANNEL, json.dumps([
            self.get_argument('part'),
            self.get_argument('action'),
        ]))


class SensorsHandler(tornado.websocket.WebSocketHandler):
    """Sensors handler"""

    def __init__(self, *args, **kwargs):
        super(SensorsHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, REDIS_CHANNEL)
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))


class WebApp(tornado.web.Application):
    """Web app"""

    def __init__(self, **kwargs):
        path = os.path.abspath(os.path.dirname(__file__))
        self.client = tornadoredis.Client()
        self.client.connect()
        super(WebApp, self).__init__(
            [
                (r'/', IndexHandler),
                (r'/arm/', ArmHandler),
                (r'/sensors/', SensorsHandler),
            ],
            template_path=os.path.join(path, '../templates'),
            static_path=os.path.join(path, '../static'),
            **kwargs
        )


def main():
    """Web target"""
    app = WebApp(debug=DEBUG)
    app.listen(PORT, HOST)
    tornado.ioloop.IOLoop.instance().start()
