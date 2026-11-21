
ROWS = 6
COLS = 7

EMPTY = 0
HUMAN = 1
COMPUTER = 2


def create_board():
    board = []

    for i in range(ROWS):
        row = [EMPTY] * COLS
        board.append(row)

    return board


def print_board(board):
    print()

    for row in board:
        print(row)

    numbers = ""
    for col in range(COLS):
        numbers += str(col) + " "
    print(numbers)
    print()


def is_valid_move(board, col):
    return board[0][col] == EMPTY


def get_valid_moves(board):
    moves = []

    for col in range(COLS):
        if is_valid_move(board, col):
            moves.append(col)

    return moves


def drop_disc(board, col, player):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return row

    return -1


def check_winner(board, player):
    # Check horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if (
                board[row][col] == player
                and board[row][col + 1] == player
                and board[row][col + 2] == player
                and board[row][col + 3] == player
            ):
                return True

    # Check vertical
    for row in range(ROWS - 3):
        for col in range(COLS):
            if (
                board[row][col] == player
                and board[row + 1][col] == player
                and board[row + 2][col] == player
                and board[row + 3][col] == player
            ):
                return True

    # Check diagonal from top-left to bottom-right
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if (
                board[row][col] == player
                and board[row + 1][col + 1] == player
                and board[row + 2][col + 2] == player
                and board[row + 3][col + 3] == player
            ):
                return True

    # Check diagonal from bottom-left to top-right
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if (
                board[row][col] == player
                and board[row - 1][col + 1] == player
                and board[row - 2][col + 2] == player
                and board[row - 3][col + 3] == player
            ):
                return True

    return False


def is_board_full(board):
    for col in range(COLS):
        if board[0][col] == EMPTY:
            return False

    return True




def count_connected_fours(board, player):
    count = 0

    # Horizontal
    for row in range(ROWS):
        for col in range(COLS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                count += 1

    # Vertical
    for row in range(ROWS - 3):
        for col in range(COLS):
            if all(board[row + i][col] == player for i in range(4)):
                count += 1

    # Diagonal: top-left to bottom-right
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            if all(board[row + i][col + i] == player for i in range(4)):
                count += 1

    # Diagonal: bottom-left to top-right
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            if all(board[row - i][col + i] == player for i in range(4)):
                count += 1

    return count
