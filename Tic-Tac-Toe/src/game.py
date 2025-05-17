import tkinter as tk
from tkinter import messagebox
import logging
from typing import Optional
from src.board import Board
from src.player import Player
from src.ai import AI
from src.stats import GameStats
from src.cell_state import CellState
from functools import wraps

logging.basicConfig(filename="game.log", level=logging.INFO, format="%(asctime)s - %(message)s")

class TicTacToe:
    def __init__(self, root: tk.Tk, mode: str = "pvp"):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.board = Board()
        self.stats = GameStats("stats.json")
        self.mode = mode
        self.player1 = Player("Player 1", CellState.X)
        self.player2 = Player("Player 2", CellState.O) if mode == "pvp" else Player("AI", CellState.O, is_ai=True)
        self.current_player = self.player1
        self.ai = AI(CellState.O) if mode == "pve" else None
        respuesta = self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.setup_gui()

    def setup_gui(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Menu frame
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(pady=10)

        tk.Button(menu_frame, text="Play PvP", command=lambda: self.start_game("pvp"), font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(menu_frame, text="Play vs AI", command=lambda: self.start_game("pve"), font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(menu_frame, text="View Stats", command=self.show_stats, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(menu_frame, text="Exit", command=self.root.quit, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(self.root, text=f"{self.current_player.name}'s Turn ({self.current_player.symbol.value})", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)

        # Board frame
        board_frame = tk.Frame(self.root)
        board_frame.pack()

        # Create 3x3 grid of buttons
        for row in range(3):
            for col in range(3):
                button = tk.Button(board_frame, text="", font=("Arial", 20, "bold"), width=5, height=2,
                                   command=lambda r=row, c=col: self.play_move(r, c))
                button.grid(row=row, column=col, padx=5, pady=5)
                self.buttons[row][col] = button

        # New game button
        tk.Button(self.root, text="New Game", command=self.reset_game, font=("Arial", 12)).pack(pady=10)

    def log_move(func):
        """Decorator to log player moves."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if result:
                logging.info(f"{self.current_player.name} placed {self.current_player.symbol.value} at position ({args[0]}, {args[1]})")
            return result
        return wrapper

    @log_move
    def play_move(self, row: int, col: int) -> bool:
        """Play a move and update GUI."""
        if self.board.place_move(row, col, self.current_player.symbol):
            # Update button text and color
            symbol = self.current_player.symbol.value
            color = "red" if self.current_player.symbol == CellState.X else "blue"
            self.buttons[row][col].config(text=symbol, fg=color, state="disabled")

            # Check for winner or draw
            winner = self.board.has_winner()
            if winner:
                self.status_label.config(text=f"{self.current_player.name} Wins!")
                messagebox.showinfo("Game Over", f"{self.current_player.name} Wins!")
                self.stats.update_stats(self.current_player.name)
                self.disable_board()
                return True

            if self.board.is_full():
                self.status_label.config(text="It's a Draw!")
                messagebox.showinfo("Game Over", "It's a Draw!")
                self.stats.update_stats("draw")
                self.disable_board()
                return True

            # Switch player
            self.current_player = self.player2 if self.current_player == self.player1 else self.player1
            self.status_label.config(text=f"{self.current_player.name}'s Turn ({self.current_player.symbol.value})")

            # If AI's turn, make AI move
            if self.mode == "pve" and self.current_player.is_ai:
                self.root.after(500, self.play_ai_move)  # Delay for better UX
            return True
        return False

    def play_ai_move(self):
        """Make AI move."""
        row, col = self.ai.get_move(self.board)
        self.play_move(row, col)

    def disable_board(self):
        """Disable all board buttons."""
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(state="disabled")

    def start_game(self, mode: str):
        """Start a new game with given mode."""
        self.__init__(self.root, mode)

    def reset_game(self):
        """Reset the game."""
        self.__init__(self.root, self.mode)

    def show_stats(self):
        """Show game stats."""
        stats = self.stats.stats
        message = (f"Stats:\nPlayer 1 Wins: {stats['player1_wins']}\n"
                   f"Player 2/AI Wins: {stats['player2_wins']}\nDraws: {stats['draws']}")
        messagebox.showinfo("Game Stats", message)