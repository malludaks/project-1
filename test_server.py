import unittest
import requests

class TestJWKS(unittest.TestCase):
    BASE_URL = "http://localhost:8080"

    def test_jwks(self):
        response = requests.get(f"{self.BASE_URL}/.well-known/jwks.json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("keys", response.json())

    def test_auth(self):
        response = requests.post(f"{self.BASE_URL}/auth", json={"username": "user1", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

if __name__ == "__main__":
    unittest.main()
