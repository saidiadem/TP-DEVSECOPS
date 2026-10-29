import unittest
from app import app


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_greeting(self):
        response = self.client.get("/?name=Adem")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bonjour Adem", response.data)

    def test_missing_route(self):
        self.assertEqual(self.client.get("/absent").status_code, 404)
