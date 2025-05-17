from src.cell_state import CellState

class Player:
    def __init__(self, name: str, symbol: CellState, is_ai: bool = False):
        self.name = name
        self.symbol = symbol
        self.is_ai = is_ai