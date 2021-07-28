"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

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
    """
    numberOfX, numberOfO = 0, 0

    # count number of turns x and o took
    for row in board:
        for square in row:
            if square == X:
                numberOfX += 1
            elif square == O:
                numberOfO += 1

    # based on turns return x or o
    if numberOfO >= numberOfX:
        return X
    elif numberOfX > numberOfO:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = []

    for y in range(len(board)):
        for x in range(len(board[0])):
            if not board[y][x]:
                actions.append((y, x))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # copy of board to change and return
    boardCopy = deepcopy(board)

    # assign new value based on who is going (if nothing in spot)
    if not boardCopy[action[0]][action[1]]:
        boardCopy[action[0]][action[1]] = player(board)
        return boardCopy
    else:  # else raise exception
        raise Exception("Not a valid action")

def winner(board):

    """
    Returns the winner of the game, if there is one.
    """
    # check for row wins
    for i in range(len(board)):
        if board[i][0] == X and board[i][1] == X and board[i][2] == X:
            return X
        elif board[i][0] == O and board[i][1] == O and board[i][2] == O:
            return O

    # check for column wins
    for i in range(len(board)):
        if board[0][i] == X and board[1][i] == X and board[2][i] == X:
            return X
        elif board[0][i] == O and board[1][i] == O and board[2][i] == O:
            return O

    # diagonal wins
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    elif board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return O

    if board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X
    elif board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return O
    # else no wins
    return None

def terminal(board):

    """
    Returns True if game is over, False otherwise.
    """
    # if someone one return
    if winner(board):
        return True
    # else if one square is not filled then not done yet
    for row in board:
        for square in row:
            if not square:
                return False
    # otherwise game is over, all squares filled
    return True

def utility(board):

    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    victor = winner(board)
    if victor == X:
        return 1
    elif victor == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    possibleActions = actions(board)
    currentPlayer = player(board)

    bestAction = None
    bestValue = -10 if currentPlayer == X else 10

    # look through each action
    for action in possibleActions:
        # find best action if opponent plays efficiently
        if currentPlayer == X:
            v = min(result(board, action))
            if v > bestValue:
                bestValue = v
                bestAction = action
        elif currentPlayer == O:
            v = max(result(board, action))
            if v < bestValue:
                bestValue = v
                bestAction = action

    return bestAction

def min(board):

    # once the function recurses to filled board it'll return value of action
    if terminal(board):
        return utility(board)

    possibleActions = actions(board)
    v = 10

    # look through each action
    for action in possibleActions:
        # find best number if opponent plays efficiently
        value = max(result(board, action))
        # keep the best values
        if value < v:
            v = value
        elif value > v:
            break

    return v

def max(board):
    # once the function recurses to filled board it'll return value of action
    if terminal(board):
        return utility(board)

    possibleActions = actions(board)
    v = -10

    # look through each action
    for action in possibleActions:
        # find best number if opponent plays efficiently
        value = min(result(board, action))
        # keep the best values
        if value > v:
            v = value
        elif value < v:
            """ if there is a value lower than the current one
            we know the min player (if playing optimally) will pick that,
            so don't bother looking at the rest of the actions because
            either way min player wants low action"""
            break
    return v
