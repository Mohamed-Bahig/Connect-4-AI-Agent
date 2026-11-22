# Expected Minimax for Connect Four.
#
# Level order in the tree (repeats every turn):
#   decision node (MAX = computer / MIN = human) -> chooses a column
#   chance node   (one per chosen column)        -> disc lands in the chosen column with p = 0.6,
#                                                   in the left / right neighbour with p = 0.2 each
#                                                   (0.4 for the only neighbour if one side is
#                                                   missing or full)
#   outcome node  (one per landing column)       -> board after the disc dropped, then the next
#                                                   decision node (or a leaf)
# The tree is cut after K decision levels (depth) and the board is scored with the heuristic.
# If the board is full the real score is used: (computer fours - human fours) * WIN_SCORE.

from dataclasses import dataclass, field
from time import perf_counter

from board import (
    COLS,
    COMPUTER,
    HUMAN,
    PLAYER_NAMES,
    board_is_full,
    count_connected_fours,
    drop_disc,
    next_player,
    valid_moves,
)
from heuristic import evaluate_board

WIN_SCORE = 100_000


@dataclass
class TreeNode:
    label: str
    kind: str  # "decision", "chance", "outcome" or "leaf"
    value: float = 0
    board: list | None = None
    move: int | None = None
    children: list = field(default_factory=list)


@dataclass
class SearchResult:
    move: int | None
    value: float
    tree: TreeNode | None
    nodes_expanded: int  # decision nodes expanded (MAX + MIN)
    chance_nodes: int
    leaf_nodes: int
    elapsed_seconds: float
    move_values: dict  # column -> expected value at the root

    @property
    def total_nodes(self):
        return self.nodes_expanded + self.chance_nodes + self.leaf_nodes


def chance_outcomes(board, chosen_column):
    # Return the possible landing columns and their probabilities.
    moves = valid_moves(board)
    if chosen_column not in moves:
        raise ValueError(f"Column {chosen_column} is not available")

    neighbors = [column for column in (chosen_column - 1, chosen_column + 1)
                 if column in moves]
    if len(neighbors) == 2:
        return [(chosen_column, 0.6), (neighbors[0], 0.2), (neighbors[1], 0.2)]
    if len(neighbors) == 1:
        return [(chosen_column, 0.6), (neighbors[0], 0.4)]
    return [(chosen_column, 1.0)]


def _terminal_score(board):
    difference = (
        count_connected_fours(board, COMPUTER)
        - count_connected_fours(board, HUMAN)
    )
    return difference * WIN_SCORE


def _search(board, player, depth, stats, build_tree):
    # Precondition: the board is not full and depth >= 1.
    # Returns (value, tree node or None, {column: expected value}).
    maximizing = player == COMPUTER
    stats["decision"] += 1
    node = None
    if build_tree:
        name = "MAX" if maximizing else "MIN"
        node = TreeNode(f"{name} decision - {PLAYER_NAMES[player]} to move, K left = {depth}", "decision")

    best_value = float("-inf") if maximizing else float("inf")
    move_values = {}

    for chosen_column in valid_moves(board):
        stats["chance"] += 1
        chance_node = None
        if build_tree:
            chance_node = TreeNode(f"Choose column {chosen_column} -> chance node", "chance",
                                   move=chosen_column)
        expected_value = 0.0

        for actual_column, probability in chance_outcomes(board, chosen_column):
            next_board = drop_disc(board, actual_column, player)
            label = f"Disc lands in column {actual_column} (p={probability:.1f})"

            if board_is_full(next_board) or depth == 1:
                stats["leaf"] += 1
                if board_is_full(next_board):
                    child_value = _terminal_score(next_board)
                    label += " - full board, final score"
                else:
                    child_value = evaluate_board(next_board)
                    label += " - depth limit, heuristic"
                outcome = (TreeNode(label, "leaf", child_value, next_board)
                           if build_tree else None)
            else:
                child_value, child_node, _ = _search(
                    next_board, next_player(player), depth - 1, stats, build_tree
                )
                outcome = None
                if build_tree:
                    outcome = TreeNode(label, "outcome", child_value, children=[child_node])

            expected_value += probability * child_value
            if build_tree:
                chance_node.children.append(outcome)

        move_values[chosen_column] = expected_value
        if build_tree:
            chance_node.value = expected_value
            node.children.append(chance_node)
        best_value = max(best_value, expected_value) if maximizing else min(best_value, expected_value)

    if build_tree:
        node.value = best_value
    return best_value, node, move_values


def find_best_move(board, depth, player=COMPUTER, build_tree=True):
    # Search the tree and return the best move and search details.
    # build_tree=False skips creating TreeNode objects (used by the benchmark so that
    # only the algorithm itself is timed).
    if depth < 1:
        raise ValueError("Depth must be at least 1")
    if board_is_full(board):
        raise ValueError("Cannot choose a move on a full board")

    stats = {"decision": 0, "chance": 0, "leaf": 0}
    start = perf_counter()
    value, tree, move_values = _search(board, player, depth, stats, build_tree)
    elapsed = perf_counter() - start

    # Best column; ties go to the column closest to the center, then the lowest index.
    center = (COLS - 1) / 2
    pick = max if player == COMPUTER else min
    best_value = pick(move_values.values())
    candidates = [c for c, v in move_values.items() if v == best_value]
    best_move = min(candidates, key=lambda c: (abs(c - center), c))

    return SearchResult(best_move, value, tree, stats["decision"], stats["chance"],
                        stats["leaf"], elapsed, move_values)
