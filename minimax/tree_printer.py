
from game import ROWS, COLS


def print_tree_board(board, indent=""):
    symbols = {
        0: ".",
        1: "H",
        2: "C"
    }

    for row in range(ROWS):
        line = indent

        for col in range(COLS):
            line += symbols[board[row][col]] + " "

        print(line)

    # column numbers under the board
    numbers = ""
    for col in range(COLS):
        numbers += str(col) + " "
    print(indent + numbers)


def print_leaf(board, score, indent=""):
    print(indent + "Leaf Node")
    print_tree_board(board, indent + "  ")
    print(indent + "Heuristic Value:", score)
