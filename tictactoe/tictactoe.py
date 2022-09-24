"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    If count of X equals to O in the board then its x's turn
    """
    xcounter = 0
    ocounter = 0
    for row in range(3):
        for column in range(3):
            if board[row][column] == X:
                xcounter += 1
            elif board[row][column] == O:
                ocounter += 1
    return X if xcounter == ocounter else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    Checking all board if there is no X or O on that specific coordinate,
    adding it to possible moves
    """
    possible_moves = set()
    for row in range(3):
        for column in range(3):
            if board[row][column] == EMPTY:
                possible_moves.add((row, column))
    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    (x, y) = action
    # Checking If move already made
    if board[x][y] != EMPTY:
        raise IndexError()
    # Look
    resultboard = [i[:] for i in board]
    resultboard[x][y] = player(board)
    return resultboard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Checking 3 in a row
    for row in range(3):
        if board[row][0] == board[row][1] and board[row][1] == board[row][2]:
            return board[row][1]
    # Checking 3 in a column
    for column in range(3):
        if board[0][column] == board[1][column] and board[1][column] == board[2][column]:
            return board[1][column]
    # Checking left top to right bottom cross
    if board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[1][1]
    # Checking right top to left bottom cross
    if board[0][2] == board[1][1] and board[1][1] == board[2][0]:
        return board[1][1]


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Getting winner if there is one
    take = winner(board)
    if take == X or take == O:
        return True
    # Checking if there is empty space in board
    for row in range(3):
        for column in range(3):
            if board[row][column] == EMPTY:
                return False
    # If no winner and no empty space then it's tie
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    localwinner = winner(board)
    if localwinner == X:
        return 1
    elif localwinner == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # If game is over, stop
    if terminal(board):
        return None

    elif player(board) == X:
        arr = []
        for action in actions(board):
            # Thinking about what my rival will make if i do that move
            rival = minvalue(result(board, action))
            # If i could certainly win with this move there is no need to explore others
            if rival == 1:
                return action
            # If i cant win certainly then looking other moves that I can make
            # Appends to array contains rival != 1 values
            arr.append([rival, action])
        # If i'm here it means there is no winning chance in optimal game so we play for a tie
        for i in arr:
            if i[0] == 0:
                return i[1]

    elif player(board) == O:
        arr = []
        for action in actions(board):
            rival = maxvalue(result(board, action))
            if rival == -1:
                return action
            arr.append([rival, action])
        for i in arr:
            if i[0] == 0:
                return i[1]


def maxvalue(board):
    # If game is over, stop
    if terminal(board):
        return utility(board)
    v = -500
    for action in actions(board):
        # Thinking about what my rival will make if i do that move
        rival = minvalue(result(board, action))
        # If i could certainly win with this move there is no need to explore others
        if rival == 1:
            return 1
        # If rival rival bigger than current v we updating v becouse we need max value
        v = max(v, rival)
    # If i'm here it means there is no winning chance in optimal game so we play for a tie
    return v


def minvalue(board):
    if terminal(board):
        return utility(board)
    v = 500
    for action in actions(board):
        rival = maxvalue(result(board, action))
        if rival == -1:
            return -1
        v = min(v, rival)
    return v
