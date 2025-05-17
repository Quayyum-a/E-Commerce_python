import unittest
from src.board import Board
from src.cell_state import CellState

class TestBoard(unittest.TestCase):
    def test_initial_board_empty(self):
        board = Board()
        for row in range(3):
            for col in range(3):
                self.assertEqual(board.get_cell(row, col), CellState.EMPTY)

    def test_place_valid_move(self):
        board = Board()
        self.assertTrue(board.place_move(0, 0, CellState.X))
        self.assertEqual(board.get_cell(0, 0), CellState.X)

    def test_place_invalid_move(self):
        board = Board()
        board.place_move(0, 0, CellState.X)
        self.assertFalse(board.place_move(0, 0, CellState.O))
        self.assertEqual(board.get_cell(0, 0), CellState.X)

    def test_win_row(self):
        board = Board()
        board.place_move(0, 0, CellState.X)
        board.place_move(0, 1, CellState.X)
        board.place_move(0, 2, CellState.X)
        self.assertEqual(board.has_winner(), CellState.X)

    def test_win_column(self):
        board = Board()
        board.place_move(0, 1, CellState.O)
        board.place_move(1, 1, CellState.O)
        board.place_move(2, 1, CellState.O)
        self.assertEqual(board.has_winner(), CellState.O)

    def test_win_diagonal(self):
        board = Board()
        board.place_move(0, 0, CellState.X)
        board.place_move(1, 1, CellState.X)
        board.place_move(2, 2, CellState.X)
        self.assertEqual(board.has_winner(), CellState.X)

    def test_board_full(self):
        board = Board()
        for row in range(3):
            for col in range(3):
                board.place_move(row, col, CellState.X)
        self.assertTrue(board.is_full())

    def test_board_not_full(self):
        board = Board()
        self.assertFalse(board.is_full())



if __name__ == '__main__':
    unittest.main()
