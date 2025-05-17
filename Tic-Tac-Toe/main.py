import tkinter as tk
from src.game import TicTacToe

def main():
    root = tk.Tk()
    root.geometry("400x500")  # Set window size
    game = TicTacToe(root)
    root.mainloop()

if __name__ == "__main__":
    main()