# Connect Four board rules.
#
# The board is a list of rows (row 0 is the TOP row, row ROWS-1 is the bottom).
# To use a bigger board change ROWS / COLS below (assignment: width >= 7, length >= 6).
# Everything else (windows, heuristic center column, GUI size) adapts automatically.

ROWS = 6
COLS = 7
EMPTY = 0
HUMAN = 1
COMPUTER = 2

PLAYER_NAMES = {HUMAN: "Human", COMPUTER: "Computer"}


def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def copy_board(board):
    # Rows are flat lists of ints, so a row slice is a full (and fast) copy.
    return [row[:] for row in board]


def valid_moves(board):
    # Columns that are not full (the top cell is still empty).
    return [column for column in range(COLS) if board[0][column] == EMPTY]


def drop_disc(board, column, player):
    # Return a NEW board with the disc placed in the lowest free cell of the column.
    if not 0 <= column < COLS or board[0][column] != EMPTY:
        raise ValueError(f"Column {column} is full or out of range")
    result = copy_board(board)
    for row in range(ROWS - 1, -1, -1):
        if result[row][column] == EMPTY:
            result[row][column] = player
            return result
    raise RuntimeError("Could not place a disc in a valid column")


def board_is_full(board):
    return all(cell != EMPTY for cell in board[0])


def _build_windows():
    # Every group of four cells in a line (horizontal, vertical, two diagonals),
    # stored once as coordinates so we do not rebuild them for every evaluation.
    windows = []
    for row in range(ROWS):
        for col in range(COLS):
            if col + 3 < COLS:
                windows.append(tuple((row, col + i) for i in range(4)))
            if row + 3 < ROWS:
                windows.append(tuple((row + i, col) for i in range(4)))
            if row + 3 < ROWS and col + 3 < COLS:
                windows.append(tuple((row + i, col + i) for i in range(4)))
            if row + 3 < ROWS and col - 3 >= 0:
                windows.append(tuple((row + i, col - i) for i in range(4)))
    return windows


WINDOWS = _build_windows()


def four_cell_windows(board):
    # Cell values of every group of four.
    for window in WINDOWS:
        yield [board[r][c] for r, c in window]


def count_connected_fours(board, player):
    # Number of completed groups of four for one player.
    return sum(
        all(board[r][c] == player for r, c in window) for window in WINDOWS
    )


def next_player(player):
    return HUMAN if player == COMPUTER else COMPUTER
