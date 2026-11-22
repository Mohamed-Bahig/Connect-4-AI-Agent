# Measure Expected Minimax time and node counts at different K values.
# Usage:  python benchmark.py            (K = 1..4)
#         python benchmark.py 1 2 3      (chosen K values)

import csv
import sys
from time import perf_counter

from algorithms.expectiminimax import find_best_move
from board import COMPUTER, HUMAN, create_board, drop_disc


def play(columns):
    # Build a position by alternating discs, human first.
    board = create_board()
    player = HUMAN
    for column in columns:
        board = drop_disc(board, column, player)
        player = COMPUTER if player == HUMAN else HUMAN
    return board


def sample_positions():
    return {
        "empty": create_board(),
        "early": play((3, 3, 2, 4, 4, 2)),
        "middle": play((3, 3, 2, 4, 4, 2, 5, 1, 1, 5, 0, 6, 3, 2, 2, 4, 3, 4)),
    }


def run_benchmarks(depths=(1, 2, 3, 4), csv_path="benchmark_results.csv"):
    header = ["position", "K", "seconds", "decision_nodes", "chance_nodes", "leaf_nodes",
              "best_column", "expected_value"]
    rows = []
    print(",".join(header))
    for name, board in sample_positions().items():
        for depth in depths:
            start = perf_counter()
            # build_tree=False -> only the algorithm is timed, not the tree printing structures
            result = find_best_move(board, depth, COMPUTER, build_tree=False)
            elapsed = perf_counter() - start
            row = [name, depth, f"{elapsed:.4f}", result.nodes_expanded, result.chance_nodes,
                   result.leaf_nodes, result.move, f"{result.value:.2f}"]
            rows.append(row)
            print(",".join(str(x) for x in row), flush=True)
    with open(csv_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"\nSaved to {csv_path}")


if __name__ == "__main__":
    ks = tuple(int(a) for a in sys.argv[1:]) or (1, 2, 3, 4)
    run_benchmarks(ks)
