
from game import ROWS, COLS, HUMAN, COMPUTER


# give a score to 4 cells next to each other
# positive is good for computer, negative is good for human
def evaluate_window(window):
    score = 0

    computer_count = window.count(COMPUTER)
    human_count = window.count(HUMAN)
    empty_count = window.count(0)

    # Computer is close to winning
    if computer_count == 4:
        score += 100

    elif computer_count == 3 and empty_count == 1:
        score += 10

    elif computer_count == 2 and empty_count == 2:
        score += 5

    # Human is close to winning
    if human_count == 4:
        score -= 100

    elif human_count == 3 and empty_count == 1:
        score -= 10

    elif human_count == 2 and empty_count == 2:
        score -= 5

    return score


def evaluate_board(board):
    score = 0

    # Prefer the center column
    center_col = COLS // 2
    center_count = 0

    for row in range(ROWS):
        if board[row][center_col] == COMPUTER:
            center_count += 1
        elif board[row][center_col] == HUMAN:
            center_count -= 1

    score += center_count * 3

    # Check horizontal windows
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = [
                board[row][col],
                board[row][col + 1],
                board[row][col + 2],
                board[row][col + 3]
            ]

            score += evaluate_window(window)

    # Check vertical windows
    for row in range(ROWS - 3):
        for col in range(COLS):
            window = [
                board[row][col],
                board[row + 1][col],
                board[row + 2][col],
                board[row + 3][col]
            ]

            score += evaluate_window(window)

    # Check diagonal (top-left to bottom-right)
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [
                board[row][col],
                board[row + 1][col + 1],
                board[row + 2][col + 2],
                board[row + 3][col + 3]
            ]

            score += evaluate_window(window)

    # Check diagonal (bottom-left to top-right)
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [
                board[row][col],
                board[row - 1][col + 1],
                board[row - 2][col + 2],
                board[row - 3][col + 3]
            ]

            score += evaluate_window(window)

    return score
