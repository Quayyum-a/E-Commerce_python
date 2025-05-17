import unittest
from src.player import Player
from src.cell_state import CellState

class TestPlayer(unittest.TestCase):
    def test_player_initialization(self):
        player = Player("Player 1", CellState.X)
        self.assertEqual(player.name, "Player 1")
        self.assertEqual(player.symbol, CellState.X)
        self.assertFalse(player.is_ai)

    def test_ai_player(self):
        player = Player("AI", CellState.O, is_ai=True)
        self.assertTrue(player.is_ai)