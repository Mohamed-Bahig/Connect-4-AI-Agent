# Minimax with alpha-beta pruning 
# The computer is MAX, the human is MIN. The search stops after K levels
# and uses the heuristic on the boards at that level.

from time import perf_counter

from board import (
    COLS,
    COMPUTER,
    HUMAN,
    ROWS,
    board_is_full,
    count_connected_fours,
    drop_disc,
    four_cell_windows,
    valid_moves,
)

WIN_SCORE = 100_000   # value of a finished board, per connected-four of difference


class AlphaBetaResult:
    # what the GUI needs from a search: the chosen column + info for printing
    def __init__(self, move, value, nodes, lines, elapsed_seconds=0.0):
        self.move = move
        self.value = value
        self.nodes = nodes      # number of nodes expanded
        self.elapsed_seconds = elapsed_seconds
        self.lines = lines      # list of (level, text) used to print the tree


# ------------------------------------------------------------------
# Heuristic
# ------------------------------------------------------------------
def heuristic(board):
    # bigger = better for the computer, smaller = better for the human
    # 1. difference in connected-fours already made
    # 2. open groups of 4 (no opponent disc) that have 3 or 2 of our discs
    # 3. small bonus for the centre column
    score = 100 * (count_connected_fours(board, COMPUTER) -
                   count_connected_fours(board, HUMAN))

    for w in four_cell_windows(board):
        c = w.count(COMPUTER)
        h = w.count(HUMAN)
        e = w.count(0)
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
        if board[r][mid] == COMPUTER:
            score += 3
        elif board[r][mid] == HUMAN:
            score -= 3
    return score


# ------------------------------------------------------------------
# Alpha-beta search
# ------------------------------------------------------------------
nodes_expanded = 0


def final_score(board):
    # the board is full: the real result decides (more fours wins)
    return WIN_SCORE * (count_connected_fours(board, COMPUTER) -
                        count_connected_fours(board, HUMAN))


def alphabeta(board, depth, alpha, beta, maximizing, lines, level):
    """depth = levels left, level = how deep we are (for printing)."""
    global nodes_expanded
    nodes_expanded += 1

    if board_is_full(board):
        return final_score(board)
    if depth == 0:
        return heuristic(board)

    moves = valid_moves(board)
    player = COMPUTER if maximizing else HUMAN
    best = float('-inf') if maximizing else float('inf')

    for i, col in enumerate(moves):
        child = drop_disc(board, col, player)   # drop_disc returns a new board
        lines.append(None)              # reserve the line, fill it after the child returns
        idx = len(lines) - 1
        val = alphabeta(child, depth - 1, alpha, beta, not maximizing, lines, level + 1)
        kind = "MIN" if maximizing else "MAX"
        who = "C" if maximizing else "H"
        note = ""
        if board_is_full(child):
            note = "  (final score)"
        elif depth - 1 == 0:
            note = "  (heuristic)"
        lines[idx] = (level + 1, f"{kind} node ({who} played col {col}) value={val}{note}  [a={alpha}, b={beta}]")

        if maximizing:
            best = max(best, val)
            alpha = max(alpha, best)
        else:
            best = min(best, val)
            beta = min(beta, best)

        if alpha >= beta:
            for rest in moves[i + 1:]:
                lines.append((level + 1, f"col {rest} PRUNED (a={alpha} >= b={beta})"))
            break
    return best


def find_best_move(board, depth, player=COMPUTER):
    """Same call as the other algorithms: returns a result with .move"""
    global nodes_expanded
    nodes_expanded = 0
    lines = []
    start = perf_counter()
    alpha = float('-inf')
    beta = float('inf')
    best_val = float('-inf')
    best_col = None
    center = (COLS - 1) / 2

    for col in valid_moves(board):
        child = drop_disc(board, col, COMPUTER)
        lines.append(None)
        idx = len(lines) - 1
        val = alphabeta(child, depth - 1, alpha, beta, False, lines, 1)
        note = ""
        if board_is_full(child):
            note = "  (final score)"
        elif depth - 1 == 0:
            note = "  (heuristic)"
        lines[idx] = (1, f"MIN node (C played col {col}) value={val}{note}  [a={alpha}, b={beta}]")
        # better value wins; on a tie prefer the column closer to the centre
        if best_col is None or val > best_val or \
                (val == best_val and abs(col - center) < abs(best_col - center)):
            best_val = val
            best_col = col
        alpha = max(alpha, best_val)

    return AlphaBetaResult(best_col, best_val, nodes_expanded, lines,
                           perf_counter() - start)


# ------------------------------------------------------------------
# Tree printing
# ------------------------------------------------------------------
def tree_text(result, depth, max_levels=None):
    # max_levels = None prints the whole tree, otherwise only the first levels
    out = [f"---- Alpha-beta tree (K={depth}) ----",
           f"MAX root (computer to move) -> best value={result.value}, chosen col={result.move}"]
    for level, text in result.lines:
        if max_levels is None or level <= max_levels:
            out.append("    " * level + text)
    out.append(f"Nodes expanded: {result.nodes}  |  time: {result.elapsed_seconds:.4f} s")
    return "\n".join(out)


def print_search_result(result, depth, max_levels=None):
    print(tree_text(result, depth, max_levels))


def save_tree(result, depth, path):
    with open(path, "w") as f:
        f.write(tree_text(result, depth, None) + "\n")
