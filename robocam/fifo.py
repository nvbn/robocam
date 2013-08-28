import tornado.web
import tornado.ioloop
from . import const


class FifoHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.set_header('Content-type', 'image/jpeg')
        with open(const.FIFO_PATH) as img:
            self.write(img.read())


def main():
    app = tornado.web.Application([
        (r'/img/', FifoHandler),
    ])
    app.listen(9090)
    tornado.ioloop.IOLoop.instance().start()
