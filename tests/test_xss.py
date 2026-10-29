import unittest
from app import app


class XssRegressionTests(unittest.TestCase):
    def test_user_input_is_escaped(self):
        payload = '<script>alert(1)</script>'
        response = app.test_client().get('/', query_string={'name': payload})
        self.assertNotIn(payload.encode(), response.data)
        self.assertIn(b'&lt;script&gt;', response.data)
        self.assertIn("default-src 'none'", response.headers['Content-Security-Policy'])
