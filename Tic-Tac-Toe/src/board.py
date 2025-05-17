from typing import List, Optional
from colorama import Fore, Style
from src.cell_state import CellState

class Board:
    def __init__(self):
        self._size = 3
        self._cells: List[List[CellState]] = [[CellState.EMPTY for _ in range(self._size)] for _ in range(self._size)]

    def get_cell(self, row: int, col: int) -> CellState:
        return self._cells[row][col]

    def place_move(self, row: int, col: int, state: CellState) -> bool:
        if 0 <= row < self._size and 0 <= col < self._size:
            if state == CellState.EMPTY or self._cells[row][col] == CellState.EMPTY:
                self._cells[row][col] = state
                return True
        return False

    def has_winner(self) -> Optional[CellState]:
        # Check rows
        for row in range(self._size):
            if self._cells[row][0] != CellState.EMPTY and self._cells[row][0] == self._cells[row][1] == self._cells[row][2]:
                return self._cells[row][0]
        # Check columns
        for col in range(self._size):
            if self._cells[0][col] != CellState.EMPTY and self._cells[0][col] == self._cells[1][col] == self._cells[2][col]:
                return self._cells[0][col]
        # Check diagonals
        if self._cells[0][0] != CellState.EMPTY and self._cells[0][0] == self._cells[1][1] == self._cells[2][2]:
            return self._cells[0][0]
        if self._cells[0][2] != CellState.EMPTY and self._cells[0][2] == self._cells[1][1] == self._cells[2][0]:
            return self._cells[0][2]
        return None

    def is_full(self) -> bool:
        return all(self._cells[row][col] != CellState.EMPTY for row in range(self._size) for col in range(self._size))

    def display(self) -> None:
        for row in range(self._size):
            line = []
            for col in range(self._size):
                cell = self._cells[row][col]
                if cell == CellState.X:
                    line.append(f"{Fore.RED}{cell.value}{Style.RESET_ALL}")
                elif cell == CellState.O:
                    line.append(f"{Fore.BLUE}{cell.value}{Style.RESET_ALL}")
                else:
                    line.append(str(row * self._size + col + 1))
                line.append(" | ")
            print("".join(line))
            if row < self._size - 1:
                print("-" * (self._size * 4 - 1))