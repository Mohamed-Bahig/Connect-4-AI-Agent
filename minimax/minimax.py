
import time

from game import (
    HUMAN, COMPUTER,
    get_valid_moves, drop_disc,
    is_board_full, count_connected_fours
)

from heuristic import evaluate_board
from tree_printer import print_leaf, print_tree_board


nodes_expanded = 0
time_taken = 0


def minimax(board, depth, k, maximizing_player, indent=""):

    global nodes_expanded

    # The game ends only when the board is full
    if is_board_full(board):

        computer_score = count_connected_fours(board, COMPUTER)
        human_score = count_connected_fours(board, HUMAN)

        score = (computer_score - human_score) * 100000

        print(indent + "BOARD FULL")
        print(indent + "Computer connected-fours:", computer_score)
        print(indent + "Human connected-fours:", human_score)
        print(indent + "Final Score:", score)

        return score, None

    # Stop searching when we reach depth K
    if depth == k:

        score = evaluate_board(board)
        print_leaf(board, score, indent)

        return score, None

    valid_moves = get_valid_moves(board)

    # we count a node as expanded when we generate its children
    nodes_expanded += 1

    if maximizing_player:

        best_score = float('-inf')
        best_move = None

        print(indent + "MAX Node")

        for col in valid_moves:

            new_board = [row[:] for row in board]
            drop_disc(new_board, col, COMPUTER)

            print(indent + "  Computer plays column", col)

            score, _ = minimax(
                new_board,
                depth + 1,
                k,
                False,
                indent + "    "
            )

            print(indent + "  Column", col, "-> value", score)

            if score > best_score:
                best_score = score
                best_move = col

        print(indent + "MAX chooses:", best_move, "Score:", best_score)

        return best_score, best_move

    else:

        best_score = float('inf')
        best_move = None

        print(indent + "MIN Node")

        for col in valid_moves:

            new_board = [row[:] for row in board]
            drop_disc(new_board, col, HUMAN)

            print(indent + "  Human plays column", col)

            score, _ = minimax(
                new_board,
                depth + 1,
                k,
                True,
                indent + "    "
            )

            print(indent + "  Column", col, "-> value", score)

            if score < best_score:
                best_score = score
                best_move = col

        print(indent + "MIN chooses:", best_move, "Score:", best_score)

        return best_score, best_move


def find_best_move(board, k):

    global nodes_expanded, time_taken
    nodes_expanded = 0

    print("\n========== MINIMAX TREE (K =", k, ") ==========")
    print("Current Board:")
    print_tree_board(board)
    print()

    start = time.perf_counter()

    best_score, best_move = minimax(
        board,
        0,
        k,
        True
    )

    time_taken = time.perf_counter() - start

    print("\nBest move:", best_move)
    print("Best score:", best_score)
    print("Nodes expanded:", nodes_expanded)
    print("Time taken: %.4f seconds" % time_taken)

    return best_move
