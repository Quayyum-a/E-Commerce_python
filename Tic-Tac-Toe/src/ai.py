from typing import Tuple
from src.board import Board
from src.cell_state import CellState

class AI:
    def __init__(self, symbol: CellState):
        self.symbol = symbol
        self.opponent_symbol = CellState.O if symbol == CellState.X else CellState.X

    def get_move(self, board: Board) -> Tuple[int, int]:
        best_score = float('-inf')
        best_move = None
        for row in range(board._size):
            for col in range(board._size):
                if board.get_cell(row, col) == CellState.EMPTY:
                    board.place_move(row, col, self.symbol)
                    score = self._minimax(board, 0, False)
                    board.place_move(row, col, CellState.EMPTY)
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
        if best_move is None:
            raise ValueError("No valid moves available")
        return best_move

    def _minimax(self, board: Board, depth: int, is_maximizing: bool) -> int:
        winner = board.has_winner()
        if winner == self.symbol:
            return 10 - depth
        elif winner == self.opponent_symbol:
            return depth - 10
        if board.is_full():
            return 0

        if is_maximizing:
            best_score = float('-inf')
            for row in range(board._size):
                for col in range(board._size):
                    if board.get_cell(row, col) == CellState.EMPTY:
                        board.place_move(row, col, self.symbol)
                        score = self._minimax(board, depth + 1, False)
                        board.place_move(row, col, CellState.EMPTY)
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for row in range(board._size):
                for col in range(board._size):
                    if board.get_cell(row, col) == CellState.EMPTY:
                        board.place_move(row, col, self.opponent_symbol)
                        score = self._minimax(board, depth + 1, True)
                        board.place_move(row, col, CellState.EMPTY)
                        best_score = min(score, best_score)
            return best_score