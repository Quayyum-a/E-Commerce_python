import unittest
from unittest.mock import patch
from src.utils import get_valid_input

class TestUtils(unittest.TestCase):
    @patch('builtins.input', return_value='5')
    def test_valid_input(self, mock_input):
        result = get_valid_input("Enter number: ", 1, 9)
        self.assertEqual(result, 5)

    @patch('builtins.input', side_effect=['invalid', '10', '0', '5'])
    def test_invalid_input(self, mock_input):
        result = get_valid_input("Enter number: ", 1, 9)
        self.assertEqual(result, 5)