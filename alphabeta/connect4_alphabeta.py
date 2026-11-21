# Connect 4 - Minimax with Alpha-Beta Pruning (Student 2)
# Console version: board + rules, heuristic, depth limit K, tree printing, benchmark.
#
# Rules (from the assignment): players keep playing until the board is full,
# and the winner is the one with MORE connected-fours.
# Computer = 'C' (MAX), Human = 'H' (MIN), empty = '.'

import time

ROWS = 6
COLS = 7
EMPTY = '.'
COMP = 'C'
HUMAN = 'H'

nodes_expanded = 0   # counter used for the benchmark


# ------------------------------------------------------------------
# Board and game rules
# ------------------------------------------------------------------
def new_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]   # board[0] is the top row


def copy_board(board):
    return [row[:] for row in board]


def valid_moves(board):
    # a column is playable if its top cell is empty
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def drop_disc(board, col, player):
    # returns a NEW board with the disc dropped in col
    new = copy_board(board)
    for r in range(ROWS - 1, -1, -1):          # start from bottom row
        if new[r][col] == EMPTY:
            new[r][col] = player
            break
    return new


def is_full(board):
    return len(valid_moves(board)) == 0


def get_windows(board):
    # every group of 4 consecutive cells (horizontal, vertical, 2 diagonals)
    windows = []
    for r in range(ROWS):
        for c in range(COLS):
            if c + 3 < COLS:
                windows.append([board[r][c + i] for i in range(4)])
            if r + 3 < ROWS:
                windows.append([board[r + i][c] for i in range(4)])
            if r + 3 < ROWS and c + 3 < COLS:
                windows.append([board[r + i][c + i] for i in range(4)])
            if r + 3 < ROWS and c - 3 >= 0:
                windows.append([board[r + i][c - i] for i in range(4)])
    return windows


def count_fours(board, player):
    # number of connected-fours of this player
    # (assumption: overlapping fours count separately, so 5 in a row = 2 fours)
    return sum(1 for w in get_windows(board) if w.count(player) == 4)


def print_board(board):
    print()
    for row in board:
        print(' '.join(row))
    print(' '.join(str(c) for c in range(COLS)))
    print()


# ------------------------------------------------------------------
# Heuristic
# ------------------------------------------------------------------
def heuristic(board):
    # Bigger = better for the computer, smaller = better for the human.
    # Factors:
    #  1. difference in connected-fours already made (current score)
    #  2. open windows (no opponent disc inside) with 3 or 2 of our discs
    #     -> these are candidate fours
    #  3. small bonus for discs in the centre column
    score = 0
    score += 100 * (count_fours(board, COMP) - count_fours(board, HUMAN))

    for w in get_windows(board):
        c = w.count(COMP)
        h = w.count(HUMAN)
        e = w.count(EMPTY)
        if h == 0 and c == 3 and e == 1:
            score += 5
        elif h == 0 and c == 2 and e == 2:
            score += 2
        if c == 0 and h == 3 and e == 1:
            score -= 5
        elif c == 0 and h == 2 and e == 2:
            score -= 2

    mid = COLS // 2
    for r in range(ROWS):
        if board[r][mid] == COMP:
            score += 3
        elif board[r][mid] == HUMAN:
            score -= 3
    return score


# ------------------------------------------------------------------
# Minimax with alpha-beta pruning
# ------------------------------------------------------------------
def alphabeta(board, depth, alpha, beta, maximizing, lines, indent):
    """
    depth      : levels left before we cut the tree and use the heuristic
    lines      : list of strings used to print the tree (pre-order)
    indent     : current depth in the tree (for printing)
    returns the value of the board
    """
    global nodes_expanded
    nodes_expanded += 1

    # leaf: depth limit reached or board full
    if depth == 0 or is_full(board):
        return heuristic(board)

    moves = valid_moves(board)
    if maximizing:
        best = float('-inf')
        for i, col in enumerate(moves):
            child = drop_disc(board, col, COMP)
            # reserve a line now, fill it in after we know the value
            lines.append(None)
            idx = len(lines) - 1
            val = alphabeta(child, depth - 1, alpha, beta, False, lines, indent + 1)
            lines[idx] = '    ' * (indent + 1) + \
                f"MIN node (C played col {col}) value={val}  [a={alpha}, b={beta}]"
            best = max(best, val)
            alpha = max(alpha, best)
            if alpha >= beta:
                # prune the remaining children
                for rest in moves[i + 1:]:
                    lines.append('    ' * (indent + 1) +
                                 f"col {rest} PRUNED (a={alpha} >= b={beta})")
                break
        return best
    else:
        best = float('inf')
        for i, col in enumerate(moves):
            child = drop_disc(board, col, HUMAN)
            lines.append(None)
            idx = len(lines) - 1
            val = alphabeta(child, depth - 1, alpha, beta, True, lines, indent + 1)
            lines[idx] = '    ' * (indent + 1) + \
                f"MAX node (H played col {col}) value={val}  [a={alpha}, b={beta}]"
            best = min(best, val)
            beta = min(beta, best)
            if alpha >= beta:
                for rest in moves[i + 1:]:
                    lines.append('    ' * (indent + 1) +
                                 f"col {rest} PRUNED (a={alpha} >= b={beta})")
                break
        return best


def computer_move(board, k, show_tree=True):
    """Runs alpha-beta from the root (computer to move) and returns the best column."""
    global nodes_expanded
    nodes_expanded = 0
    lines = []
    alpha = float('-inf')
    beta = float('inf')
    best_val = float('-inf')
    best_col = None

    moves = valid_moves(board)
    root_lines = ["MAX root (computer to move)"]
    for i, col in enumerate(moves):
        child = drop_disc(board, col, COMP)
        lines.append(None)
        idx = len(lines) - 1
        val = alphabeta(child, k - 1, alpha, beta, False, lines, 1)
        lines[idx] = '    ' + f"MIN node (C played col {col}) value={val}  [a={alpha}, b={beta}]"
        if val > best_val:
            best_val = val
            best_col = col
        alpha = max(alpha, best_val)
        # no cutoff at the root (beta is always +inf there)

    if show_tree:
        print("---- Minimax tree with alpha-beta (K=%d) ----" % k)
        print(root_lines[0] + f" -> best value={best_val}, chosen col={best_col}")
        for l in lines:
            print(l)
        print("Nodes expanded:", nodes_expanded)
    return best_col


# ------------------------------------------------------------------
# Play human vs computer in the console (until the board is full)
# ------------------------------------------------------------------
def play(k):
    board = new_board()
    while not is_full(board):
        print_board(board)
        # human turn
        col = -1
        while col not in valid_moves(board):
            try:
                col = int(input("Your move (column 0-%d): " % (COLS - 1)))
            except ValueError:
                col = -1
        board = drop_disc(board, col, HUMAN)
        if is_full(board):
            break
        # computer turn
        col = computer_move(board, k)
        print("Computer plays column", col)
        board = drop_disc(board, col, COMP)

    print_board(board)
    c, h = count_fours(board, COMP), count_fours(board, HUMAN)
    print("Computer fours:", c, " Human fours:", h)
    print("Computer wins!" if c > h else "Human wins!" if h > c else "Draw!")


# ------------------------------------------------------------------
# Benchmark: time and nodes expanded for different K
# ------------------------------------------------------------------
def benchmark():
    # position 1: empty board, position 2: a mid-game board
    empty = new_board()
    mid = new_board()
    for col, p in [(3, HUMAN), (3, COMP), (2, HUMAN), (4, COMP),
                   (4, HUMAN), (2, COMP), (1, HUMAN), (5, COMP)]:
        mid = drop_disc(mid, col, p)

    print("%-12s %-3s %-10s %-12s %-8s" % ("Position", "K", "Time(s)", "Nodes", "Move"))
    for name, b in [("empty", empty), ("mid-game", mid)]:
        for k in range(1, 8):
            start = time.time()
            move = computer_move(b, k, show_tree=False)
            t = time.time() - start
            print("%-12s %-3d %-10.4f %-12d %-8d" % (name, k, t, nodes_expanded, move))


if __name__ == "__main__":
    print("1) Play against the computer")
    print("2) Run benchmark")
    choice = input("Choose: ").strip()
    if choice == "2":
        benchmark()
    else:
        k = int(input("Enter K (depth limit): "))
        play(k)