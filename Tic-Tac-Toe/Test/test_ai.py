import unittest
from src.ai import AI
from src.board import Board
from src.cell_state import CellState

class TestAI(unittest.TestCase):
    def test_ai_blocks_win(self):
        board = Board()
        ai = AI(CellState.O)
        board.place_move(0, 0, CellState.X)
        board.place_move(0, 1, CellState.X)
        row, col = ai.get_move(board)
        self.assertEqual((row, col), (0, 2))  # AI should block X's win