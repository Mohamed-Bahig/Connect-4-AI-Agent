# Measure time and node counts of the 3 algorithms at different K values.
# Usage:  python benchmark.py            (K = 1..4)
#         python benchmark.py 1 2 3      (chosen K values)

import csv
import sys
from time import perf_counter

from algorithms import alphabeta, expectiminimax, minimax
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
    header = ["algorithm", "position", "K", "seconds", "nodes_expanded", "best_column", "value"]
    rows = []
    print(",".join(header))
    for name, board in sample_positions().items():
        for depth in depths:
            # same board and same K for all 3 algorithms
            # build_tree=False -> only the algorithm is timed, not the tree printing structures
            start = perf_counter()
            result = minimax.find_best_move(board, depth, COMPUTER, build_tree=False)
            rows.append(["minimax", name, depth, perf_counter() - start, result.nodes_expanded,
                         result.move, result.value])

            start = perf_counter()
            result = alphabeta.find_best_move(board, depth, COMPUTER)
            rows.append(["alphabeta", name, depth, perf_counter() - start, result.nodes,
                         result.move, result.value])

            start = perf_counter()
            result = expectiminimax.find_best_move(board, depth, COMPUTER, build_tree=False)
            rows.append(["expectiminimax", name, depth, perf_counter() - start, result.nodes_expanded,
                         result.move, round(result.value, 2)])

            for row in rows[-3:]:
                row[3] = f"{row[3]:.4f}"
                print(",".join(str(x) for x in row), flush=True)
    with open(csv_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"\nSaved to {csv_path}")


if __name__ == "__main__":
    ks = tuple(int(a) for a in sys.argv[1:]) or (1, 2, 3, 4)
    run_benchmarks(ks)
