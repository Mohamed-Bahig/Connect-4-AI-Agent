# Score a board from the COMPUTER's point of view.
# Bigger number = computer is closer to winning, smaller = human is closer.
#
# Factors (all symmetric: what helps the computer adds, what helps the human subtracts):
#   1. Completed connected-fours (this is what decides the winner, so it weighs most).
#   2. Windows of four that still can become a four for one side (the other side has no disc in them):
#        - 3 discs + 1 empty cell that can be played RIGHT NOW  -> immediate threat (strong)
#        - 3 discs + 1 empty cell that is not playable yet       -> future threat
#        - 2 discs + 2 empty cells                              -> potential
#   3. Positional value: discs in central columns belong to more possible fours.

from board import COLS, COMPUTER, EMPTY, HUMAN, ROWS, WINDOWS

FOUR_WEIGHT = 100
THREE_PLAYABLE = 16
THREE_OPEN = 10
TWO_OPEN = 4

# Column weights grow towards the center: for 7 columns -> [1, 2, 3, 4, 3, 2, 1]
COLUMN_WEIGHT = [min(c, COLS - 1 - c) + 1 for c in range(COLS)]


def _playable(board, row, col):
    # An empty cell can be played now if it is on the bottom row or the cell below is filled.
    return row == ROWS - 1 or board[row + 1][col] != EMPTY


def _parts(board):
    fours = threats = potential = position = 0
    for window in WINDOWS:
        cells = [board[r][c] for r, c in window]
        computer = cells.count(COMPUTER)
        human = cells.count(HUMAN)

        if computer == 4:
            fours += 1
        elif human == 4:
            fours -= 1
        elif human == 0 and computer > 0:
            sign = 1
            count = computer
        elif computer == 0 and human > 0:
            sign = -1
            count = human
        else:
            continue

        if computer == 4 or human == 4:
            continue
        if count == 3:
            empty_index = cells.index(EMPTY)
            r, c = window[empty_index]
            threats += sign * (THREE_PLAYABLE if _playable(board, r, c) else THREE_OPEN)
        elif count == 2:
            potential += sign * TWO_OPEN

    for row in board:
        for col, cell in enumerate(row):
            if cell == COMPUTER:
                position += COLUMN_WEIGHT[col]
            elif cell == HUMAN:
                position -= COLUMN_WEIGHT[col]
    return fours * FOUR_WEIGHT, threats, potential, position


def evaluate_board(board):
    # Return one number: higher = better for the computer.
    return sum(_parts(board))


def explain_board(board):
    # Same score split into its factors (useful for the report).
    fours, threats, potential, position = _parts(board)
    return {
        "connected_fours": fours,
        "threes": threats,
        "twos": potential,
        "position": position,
        "total": fours + threats + potential + position,
    }
