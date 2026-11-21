
import io
import contextlib

from game import create_board, drop_disc, HUMAN, COMPUTER
import minimax


# test boards (same boards should be used for all 3 algorithms)
def empty_board():
    return create_board()


def middle_board():
    board = create_board()
    moves = [3, 3, 2, 4, 4, 2, 5, 1]
    player = HUMAN
    for col in moves:
        drop_disc(board, col, player)
        if player == HUMAN:
            player = COMPUTER
        else:
            player = HUMAN
    return board


boards = {
    "Empty board": empty_board(),
    "Middle game": middle_board()
}

print("Algorithm: Minimax (without alpha-beta)")
print()

for name in boards:
    print(name)
    print("K\tNodes Expanded\tTime (s)")

    for k in range(1, 6):
        board = [row[:] for row in boards[name]]

        # hide the tree so printing does not affect the time
        with contextlib.redirect_stdout(io.StringIO()):
            minimax.find_best_move(board, k)

        print(str(k) + "\t" + str(minimax.nodes_expanded) + "\t\t" + "%.4f" % minimax.time_taken)

    print()
