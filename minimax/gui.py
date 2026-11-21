
import tkinter as tk
from tkinter import messagebox

from game import (
    create_board, drop_disc, get_valid_moves,
    is_board_full, count_connected_fours,
    HUMAN, COMPUTER, ROWS, COLS
)

from minimax import find_best_move


class Connect4GUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 - AI Agent")

        self.board = create_board()
        self.k = 2

        # game does not start until we press Start Game
        self.game_over = True

        # Depth selection
        tk.Label(root, text="Search Depth (K):").pack()

        self.depth_entry = tk.Entry(root)
        self.depth_entry.insert(0, "2")
        self.depth_entry.pack()

        # Algorithm selection
        tk.Label(root, text="Algorithm:").pack()

        self.algorithm = tk.StringVar(value="minimax")

        tk.Radiobutton(
            root, text="Minimax",
            variable=self.algorithm, value="minimax"
        ).pack()

        # TODO: enable these after adding alpha-beta and expectiminimax
        tk.Radiobutton(
            root, text="Minimax with Alpha-Beta",
            variable=self.algorithm, value="alphabeta",
            state="disabled"
        ).pack()

        tk.Radiobutton(
            root, text="Expected Minimax",
            variable=self.algorithm, value="expectiminimax",
            state="disabled"
        ).pack()

        self.status = tk.Label(
            root,
            text="Choose K and algorithm then press Start Game",
            font=("Arial", 14)
        )
        self.status.pack(pady=10)

        # Game board
        self.canvas = tk.Canvas(
            root,
            width=COLS * 80,
            height=ROWS * 80,
            bg="blue"
        )
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.human_move)

        self.start_button = tk.Button(
            root,
            text="Start Game",
            command=self.start_game
        )
        self.start_button.pack(pady=10)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")

        for row in range(ROWS):
            for col in range(COLS):

                x1 = col * 80 + 5
                y1 = row * 80 + 5
                x2 = x1 + 70
                y2 = y1 + 70

                if self.board[row][col] == HUMAN:
                    color = "red"
                elif self.board[row][col] == COMPUTER:
                    color = "yellow"
                else:
                    color = "white"

                self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="black"
                )

    def human_move(self, event):

        if self.game_over:
            return

        col = event.x // 80

        if col < 0 or col >= COLS:
            return

        if col not in get_valid_moves(self.board):
            return

        drop_disc(self.board, col, HUMAN)

        self.draw_board()

        if self.check_game_end():
            return

        self.status.config(text="Computer is thinking...")

        self.root.after(100, self.computer_move)

    def computer_move(self):

        if self.game_over:
            return

        if self.algorithm.get() == "minimax":
            move = find_best_move(self.board, self.k)
        else:
            move = None

        if move is None:
            self.check_game_end()
            return

        drop_disc(self.board, move, COMPUTER)

        self.draw_board()

        if self.check_game_end():
            return

        self.status.config(text="Your turn! You are Red.")


    def check_game_end(self):

        if is_board_full(self.board):

            computer_fours = count_connected_fours(self.board, COMPUTER)
            human_fours = count_connected_fours(self.board, HUMAN)

            self.game_over = True

            if computer_fours > human_fours:
                result = "Computer Wins!"

            elif human_fours > computer_fours:
                result = "You Win!"

            else:
                result = "Draw!"

            self.status.config(
                text=f"{result} Computer: {computer_fours} | You: {human_fours}"
            )

            messagebox.showinfo(
                "Game Over",
                f"{result}\n"
                f"Computer connected-fours: {computer_fours}\n"
                f"Your connected-fours: {human_fours}"
            )

            return True

        return False

    def start_game(self):

        # read K before the game begins
        try:
            new_k = int(self.depth_entry.get())

            if new_k < 1:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Depth",
                "Please enter a positive integer for K."
            )
            return

        self.k = new_k
        self.board = create_board()
        self.game_over = False

        self.status.config(text="Your turn! You are Red.")

        self.draw_board()


def main():

    root = tk.Tk()

    game = Connect4GUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
