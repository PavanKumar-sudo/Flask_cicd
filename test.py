import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestSystemMonitoring(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_high_cpu_triggers_alert(self, mock_virtual_memory, mock_cpu_percent):
        mock_cpu_percent.return_value = 90.0
        mock_mem = MagicMock()
        mock_mem.percent = 20.0
        mock_virtual_memory.return_value = mock_mem

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"High CPU or Memory Detected", response.data)

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_high_memory_triggers_alert(self, mock_virtual_memory, mock_cpu_percent):
        mock_cpu_percent.return_value = 30.0
        mock_mem = MagicMock()
        mock_mem.percent = 90.0
        mock_virtual_memory.return_value = mock_mem

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"High CPU or Memory Detected", response.data)

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_normal_usage_no_alert(self, mock_virtual_memory, mock_cpu_percent):
        mock_cpu_percent.return_value = 20.0
        mock_mem = MagicMock()
        mock_mem.percent = 30.0
        mock_virtual_memory.return_value = mock_mem

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"High CPU or Memory Detected", response.data)

if __name__ == '__main__':
    unittest.main()
