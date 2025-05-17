import json
from typing import Dict

class GameStats:
    def __init__(self, filename: str):
        self.filename = filename
        self.stats: Dict[str, int] = self._load_stats()

    def _load_stats(self) -> Dict[str, int]:
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"player1_wins": 0, "player2_wins": 0, "draws": 0}

    def update_stats(self, winner: str) -> None:
        if winner == "Player 1":
            self.stats["player1_wins"] += 1
        elif winner in ["Player 2", "AI"]:
            self.stats["player2_wins"] += 1
        else:
            self.stats["draws"] += 1
        with open(self.filename, 'w') as f:
            json.dump(self.stats, f, indent=4)