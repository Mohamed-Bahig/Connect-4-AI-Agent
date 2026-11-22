import sys

from board import COLS, COMPUTER, HUMAN


def print_board(board, indent="", out=sys.stdout):
    symbols = {0: ".", HUMAN: "H", COMPUTER: "C"}
    for row in board:
        print(indent + " ".join(symbols[cell] for cell in row), file=out)
    print(indent + " ".join(str(col) for col in range(COLS)), file=out)


def print_tree(node, max_plies=None, out=sys.stdout, chosen_move=None):
    # max_plies = how many decision levels to print (None = the whole tree).
    # Indentation shows the depth. Leaves show the board and its heuristic / final value.
    _print_node(node, "", 1, max_plies, out, chosen_move)


def _print_node(node, indent, ply, max_plies, out, chosen_move):
    if node.kind == "decision":
        if max_plies is not None and ply > max_plies:
            print(f"{indent}... {node.label}: value = {node.value:.2f}  (subtree hidden)", file=out)
            return
        print(f"{indent}{node.label}: value = {node.value:.2f}", file=out)
        next_ply = ply + 1
    elif node.kind == "chance":
        mark = "   <== CHOSEN" if ply == 1 and node.move == chosen_move else ""
        print(f"{indent}{node.label}: expected value = {node.value:.2f}{mark}", file=out)
        next_ply = ply
    elif node.kind == "outcome":
        print(f"{indent}{node.label}: value = {node.value:.2f}", file=out)
        next_ply = ply
    else:  # leaf
        print(f"{indent}{node.label}: value = {node.value:.2f}", file=out)
        print_board(node.board, indent + "    ", out)
        return

    for child in node.children:
        _print_node(child, indent + "  ", next_ply, max_plies, out, chosen_move)


def print_search_result(result, k, max_plies=None, out=sys.stdout):
    # Header, root summary, the tree and the statistics of one computer turn.
    print(f"\n=== Expected Minimax tree (K={k}) ===", file=out)
    print("Root summary (expected value per chosen column):", file=out)
    for column in sorted(result.move_values):
        mark = "  <== best" if column == result.move else ""
        print(f"  column {column}: {result.move_values[column]:.2f}{mark}", file=out)
    print("", file=out)
    print_tree(result.tree, max_plies, out, result.move)
    print(f"\nChosen column: {result.move}   root value: {result.value:.2f}", file=out)
    print(f"Decision nodes expanded: {result.nodes_expanded}  |  chance nodes: {result.chance_nodes}"
          f"  |  leaves: {result.leaf_nodes}  |  time: {result.elapsed_seconds:.4f} s", file=out)


def save_tree(result, k, path):
    # Write the complete tree to a text file.
    with open(path, "w", encoding="utf-8") as handle:
        print_search_result(result, k, None, handle)
