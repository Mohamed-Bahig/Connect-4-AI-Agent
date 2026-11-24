import random
import threading
import tkinter as tk
from tkinter import messagebox

from algorithms.expectiminimax import chance_outcomes, find_best_move
from algorithms import alphabeta
from board import (
    COLS,
    COMPUTER,
    HUMAN,
    ROWS,
    board_is_full,
    count_connected_fours,
    create_board,
    drop_disc,
    valid_moves,
)
from tree_printer import print_search_result, save_tree

CELL_SIZE = 72
BACKGROUND = "#f3f6f8"
BOARD_COLOR = "#1769aa"
PLAYER_COLORS = {HUMAN: "#e53935", COMPUTER: "#2eaa5f"}

# algorithms the player can choose from. To add Minimax (no pruning) just add a name here
# and a branch for it in start_computer_turn().
ALPHA_BETA = "Minimax with alpha-beta"
EXPECTED = "Expected Minimax"
ALGORITHMS = [ALPHA_BETA, EXPECTED]


class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)
        self.board = create_board()
        self.depth = 2
        self.current_algorithm = ALPHA_BETA   # fixed when the game starts
        self.print_plies = 2
        self.game_over = True
        self.computer_turn = False
        self.game_id = 0          # lets us ignore a search that belongs to an old game
        self.turn_number = 0
        self.pending_result = None
        self.last_landing = None  # (row, col) of the newest disc, drawn with a thick outline

        tk.Label(root, text="CONNECT FOUR", font=("Arial", 18, "bold"),
                 bg=BACKGROUND, fg="#183247").pack(pady=(14, 4))

        controls = tk.Frame(root, padx=8, pady=4, bg=BACKGROUND)
        controls.pack()
        tk.Label(controls, text="Search depth K:", bg=BACKGROUND).pack(side=tk.LEFT)
        self.depth_entry = tk.Entry(controls, width=4)
        self.depth_entry.insert(0, "2")
        self.depth_entry.pack(side=tk.LEFT, padx=(4, 10))
        tk.Label(controls, text="Tree levels to print (0 = all):", bg=BACKGROUND).pack(side=tk.LEFT)
        self.plies_entry = tk.Entry(controls, width=4)
        self.plies_entry.insert(0, "2")
        self.plies_entry.pack(side=tk.LEFT, padx=(4, 10))

        options = tk.Frame(root, padx=8, pady=2, bg=BACKGROUND)
        options.pack()
        self.algorithm = tk.StringVar(value=ALPHA_BETA)
        tk.Label(options, text="Algorithm:", bg=BACKGROUND).pack(side=tk.LEFT)
        tk.OptionMenu(options, self.algorithm, *ALGORITHMS).pack(side=tk.LEFT, padx=(4, 10))
        self.computer_first = tk.BooleanVar(value=False)
        tk.Checkbutton(options, text="Computer starts", variable=self.computer_first,
                       bg=BACKGROUND).pack(side=tk.LEFT, padx=6)
        self.save_tree_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options, text="Save full tree to file each turn", variable=self.save_tree_var,
                       bg=BACKGROUND).pack(side=tk.LEFT, padx=6)
        self.no_random = tk.BooleanVar(value=False)
        tk.Checkbutton(options, text="No random landing (testing only)", variable=self.no_random,
                       bg=BACKGROUND).pack(side=tk.LEFT, padx=6)
        tk.Button(
            options, text="Start game", command=self.start_game,
            bg="#183247", fg="white", activebackground="#294b63",
            activeforeground="white", relief=tk.FLAT, padx=12, pady=5,
        ).pack(side=tk.LEFT, padx=(8, 0))

        legend = tk.Frame(root, bg=BACKGROUND)
        legend.pack(pady=(6, 2))
        self.human_label = tk.Label(legend, text="You: 0", bg=BACKGROUND, fg=PLAYER_COLORS[HUMAN],
                                    font=("Arial", 10, "bold"))
        self.human_label.pack(side=tk.LEFT, padx=12)
        self.computer_label = tk.Label(legend, text="Computer: 0", bg=BACKGROUND,
                                       fg=PLAYER_COLORS[COMPUTER], font=("Arial", 10, "bold"))
        self.computer_label.pack(side=tk.LEFT, padx=12)

        self.status = tk.Label(
            root, text="Choose K, then start a game.", bg=BACKGROUND,
            fg="#34495e", wraplength=COLS * CELL_SIZE,
        )
        self.status.pack(pady=(0, 8))

        self.canvas = tk.Canvas(
            root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE + 22,
            bg=BOARD_COLOR, highlightthickness=0,
        )
        self.canvas.pack(padx=8, pady=8)
        self.canvas.bind("<Button-1>", self.human_move)
        self.draw_board()

    # ------------------------------------------------------------------ drawing
    def draw_board(self):
        self.canvas.delete("all")
        colors = {0: "#f8fafc", **PLAYER_COLORS}
        for row in range(ROWS):
            for col in range(COLS):
                x1 = col * CELL_SIZE + 6
                y1 = row * CELL_SIZE + 6
                newest = self.last_landing == (row, col)
                self.canvas.create_oval(
                    x1, y1, x1 + CELL_SIZE - 12, y1 + CELL_SIZE - 12,
                    fill=colors[self.board[row][col]],
                    outline="#ffd54f" if newest else "#0d4675",
                    width=5 if newest else 2,
                )
        for col in range(COLS):
            self.canvas.create_text(col * CELL_SIZE + CELL_SIZE // 2, ROWS * CELL_SIZE + 11,
                                    text=str(col), fill="white", font=("Arial", 10, "bold"))
        self.human_label.config(text=f"You: {count_connected_fours(self.board, HUMAN)}")
        self.computer_label.config(text=f"Computer: {count_connected_fours(self.board, COMPUTER)}")

    # ------------------------------------------------------------------ moves
    def _apply_random_landing(self, chosen_column, player):
        # The chosen column is only the INTENDED column: the disc may slip to a neighbour.
        # the disc only slips with Expected Minimax; the other algorithms drop it where chosen
        if self.no_random.get() or self.current_algorithm != EXPECTED:
            actual_column = chosen_column
        else:
            outcomes = chance_outcomes(self.board, chosen_column)
            columns = [column for column, _ in outcomes]
            weights = [probability for _, probability in outcomes]
            actual_column = random.choices(columns, weights=weights, k=1)[0]
        self.board = drop_disc(self.board, actual_column, player)
        for row in range(ROWS):
            if self.board[row][actual_column] != 0:
                self.last_landing = (row, actual_column)
                break
        return actual_column

    def human_move(self, event):
        if self.game_over or self.computer_turn:
            return
        chosen_column = event.x // CELL_SIZE
        if chosen_column not in valid_moves(self.board):
            return

        actual_column = self._apply_random_landing(chosen_column, HUMAN)
        self.draw_board()
        if self.finish_if_full():
            return
        if actual_column == chosen_column:
            note = f"You chose column {chosen_column}; it landed there."
        else:
            note = f"You chose column {chosen_column} but the disc slipped to column {actual_column}."
        self.status.config(text=note + " Computer is thinking...")
        self.start_computer_turn()

    def start_computer_turn(self):
        # The search runs in a worker thread so the window does not freeze for big K.
        self.computer_turn = True
        self.pending_result = None
        self.turn_number += 1
        game_id = self.game_id
        board = [row[:] for row in self.board]
        depth = self.depth
        plies = self.print_plies
        turn = self.turn_number
        save = self.save_tree_var.get()
        algorithm = self.current_algorithm

        def think():
            if algorithm == ALPHA_BETA:
                search, show, store = alphabeta.find_best_move, alphabeta.print_search_result, alphabeta.save_tree
            else:
                search, show, store = find_best_move, print_search_result, save_tree
            result = search(board, depth, COMPUTER)
            if game_id != self.game_id:
                return
            show(result, depth, plies)
            if save:
                path = f"tree_turn_{turn}.txt"
                store(result, depth, path)
                print(f"Full tree saved to {path}")
            self.pending_result = (game_id, result)

        threading.Thread(target=think, daemon=True).start()
        self.root.after(50, self.poll_computer)

    def poll_computer(self):
        if self.pending_result is None:
            if self.computer_turn:
                self.root.after(50, self.poll_computer)
            return
        game_id, result = self.pending_result
        self.pending_result = None
        if game_id != self.game_id:
            return

        actual_column = self._apply_random_landing(result.move, COMPUTER)
        self.draw_board()
        if self.finish_if_full():
            return
        self.computer_turn = False
        self.status.config(
            text=f"Computer chose column {result.move}; disc landed in column {actual_column}. Your turn.")

    # ------------------------------------------------------------------ end / start
    def finish_if_full(self):
        if not board_is_full(self.board):
            return False

        self.game_over = True
        self.computer_turn = False
        human_score = count_connected_fours(self.board, HUMAN)
        computer_score = count_connected_fours(self.board, COMPUTER)
        if computer_score > human_score:
            result = "Computer wins"
        elif human_score > computer_score:
            result = "You win"
        else:
            result = "Draw"

        message = (
            f"{result}\nHuman connected-fours: {human_score}\n"
            f"Computer connected-fours: {computer_score}"
        )
        self.status.config(text=message.replace("\n", " | "))
        messagebox.showinfo("Game over", message)
        return True

    def start_game(self):
        try:
            depth = int(self.depth_entry.get())
            plies = int(self.plies_entry.get())
            if depth < 1 or plies < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input",
                                 "K must be a positive whole number and tree levels a whole number >= 0.")
            return

        self.current_algorithm = self.algorithm.get()
        self.game_id += 1          # invalidates any search still running from the previous game
        self.depth = depth
        self.print_plies = plies if plies > 0 else None
        self.turn_number = 0
        self.board = create_board()
        self.last_landing = None
        self.game_over = False
        self.computer_turn = False
        self.pending_result = None
        self.draw_board()
        if self.computer_first.get():
            self.status.config(text="Computer is thinking...")
            self.start_computer_turn()
        else:
            self.status.config(text="Your turn. Click a column to choose where to drop a disc.")


def main():
    root = tk.Tk()
    ConnectFourGUI(root)
    root.mainloop()