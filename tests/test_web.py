from tornado.testing import AsyncHTTPTestCase
from robocam import web


class BaseWebCaseMixin(object):
    """Base case for robocam.web"""

    def get_app(self):
        return web.WebApp()


class IndexHandlerCase(BaseWebCaseMixin, AsyncHTTPTestCase):
    """Check index handler"""

    def test_get(self):
        """Test get"""
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
