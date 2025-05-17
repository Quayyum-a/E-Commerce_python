import unittest
from unittest.mock import patch
from src.game import TicTacToe
from src.cell_state import CellState

class TestGame(unittest.TestCase):
    def test_initial_player(self):
        game = TicTacToe("pvp")
        self.assertEqual(game.current_player.name, "Player 1")

    def test_play_move(self):
        game = TicTacToe("pvp")
        self.assertTrue(game.play_move(1))
        self.assertEqual(game.board.get_cell(0, 0), CellState.X)
        self.assertEqual(game.current_player.name, "Player 2")