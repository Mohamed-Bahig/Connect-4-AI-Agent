# Minimax without alpha-beta pruning
# The computer is MAX, the human is MIN. The search stops after K levels
# and uses the heuristic on the boards at that level.

from time import perf_counter

from board import (
    COLS,
    COMPUTER,
    HUMAN,
    board_is_full,
    count_connected_fours,
    drop_disc,
    valid_moves,
)
from heuristic import evaluate_board

WIN_SCORE = 100_000   # value of a full board, per connected-four of difference


class MinimaxResult:
    def __init__(self, move, value, nodes, lines, elapsed_seconds):
        self.move = move
        self.value = value
        self.nodes_expanded = nodes    # nodes whose children were generated
        self.lines = lines             # list of (level, text) used to print the tree
        self.elapsed_seconds = elapsed_seconds


nodes_expanded = 0


def final_score(board):
    # the board is full so we know the real result
    return WIN_SCORE * (count_connected_fours(board, COMPUTER) -
                        count_connected_fours(board, HUMAN))


def board_lines(board):
    symbols = {0: ".", HUMAN: "H", COMPUTER: "C"}
    lines = []
    for row in board:
        lines.append(" ".join(symbols[cell] for cell in row))
    lines.append(" ".join(str(col) for col in range(COLS)))
    return lines


def minimax(board, depth, maximizing, lines, level, build_tree):
    """depth = levels left, level = how deep we are (for printing)."""
    global nodes_expanded

    if board_is_full(board):
        score = final_score(board)
        if build_tree:
            lines.append((level, f"Leaf (full board) final score = {score}"))
        return score

    if depth == 0:
        score = evaluate_board(board)
        if build_tree:
            lines.append((level, f"Leaf heuristic value = {score}"))
            for text in board_lines(board):
                lines.append((level, "    " + text))
        return score

    # we count a node as expanded when we generate its children
    nodes_expanded += 1

    if maximizing:
        best = float('-inf')
        player = COMPUTER
    else:
        best = float('inf')
        player = HUMAN

    for col in valid_moves(board):
        child = drop_disc(board, col, player)   # drop_disc returns a new board

        if build_tree:
            # reserve the line, fill it after the child returns its value
            lines.append(None)
            idx = len(lines) - 1

        val = minimax(child, depth - 1, not maximizing, lines, level + 1, build_tree)

        if build_tree:
            kind = "MIN" if maximizing else "MAX"
            who = "C" if maximizing else "H"
            lines[idx] = (level, f"{kind} node ({who} played col {col}) value={val}")

        if maximizing:
            best = max(best, val)
        else:
            best = min(best, val)

    return best


def find_best_move(board, depth, player=COMPUTER, build_tree=True):
    """Same call as the other algorithms: returns a result with .move"""
    global nodes_expanded
    nodes_expanded = 1    # the root
    lines = []
    start = perf_counter()

    best_val = float('-inf')
    best_col = None
    center = (COLS - 1) / 2

    for col in valid_moves(board):
        child = drop_disc(board, col, COMPUTER)

        if build_tree:
            lines.append(None)
            idx = len(lines) - 1

        val = minimax(child, depth - 1, False, lines, 2, build_tree)

        if build_tree:
            lines[idx] = (1, f"MIN node (C played col {col}) value={val}")

        # better value wins, on a tie take the column closer to the centre
        if best_col is None or val > best_val or \
                (val == best_val and abs(col - center) < abs(best_col - center)):
            best_val = val
            best_col = col

    return MinimaxResult(best_col, best_val, nodes_expanded, lines,
                         perf_counter() - start)


# ------------------------------------------------------------------
# Tree printing
# ------------------------------------------------------------------
def tree_text(result, depth, max_levels=None):
    # max_levels = None prints the whole tree, otherwise only the first levels
    out = [f"---- Minimax tree (K={depth}) ----",
           f"MAX root (computer to move) -> best value={result.value}, chosen col={result.move}"]
    for level, text in result.lines:
        if max_levels is None or level <= max_levels:
            out.append("    " * level + text)
    out.append(f"Nodes expanded: {result.nodes_expanded}  |  time: {result.elapsed_seconds:.4f} s")
    return "\n".join(out)


def print_search_result(result, depth, max_levels=None):
    print(tree_text(result, depth, max_levels))


def save_tree(result, depth, path):
    with open(path, "w") as f:
        f.write(tree_text(result, depth, None) + "\n")
