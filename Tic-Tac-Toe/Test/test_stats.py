import unittest
import json
import os
from src.stats import GameStats

class TestGameStats(unittest.TestCase):
    def setUp(self):
        self.filename = "test_stats.json"
        self.stats = GameStats(self.filename)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_initial_stats(self):
        self.assertEqual(self.stats.stats, {"player1_wins": 0, "player2_wins": 0, "draws": 0})

    def test_update_stats(self):
        self.stats.update_stats("Player 1")
        with open(self.filename, 'r') as f:
            data = json.load(f)
        self.assertEqual(data["player1_wins"], 1)