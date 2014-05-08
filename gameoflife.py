"""
:Synopsis: John Conway's Game of Life, Or yet another universal machine.
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com> <elvis.dohmatob@inria.fr>

"""

import os
import time
import itertools
import numpy as np

LIVE_CHR = "*"
DEAD_CHR = " "
SCREEN_HEIGHT, SCREEN_WIDTH = map(int, os.popen('stty size', 'r').read().split())
BOARD = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=np.uint8)
NB_BOARD = np.zeros_like(BOARD)

# checks if given cell is alive or dead.
is_alive = lambda cell: BOARD[cell[0], cell[1]]

# counts number of lively neighbors of given cell.
count_neighbors_alive = lambda cell: len([n for n in get_neighbors(
            cell) if is_alive(n)])


def get_neighbors(cell):
    """
    Get (Voronoi) neighbors of given cell.

    """

    x, y = cell
    for dx, dy in itertools.product([-1, 0, 1], [-1, 0, 1]):
        if dx ** 2 + dy ** 2 > 0: yield ((x + dx) % BOARD.shape[0],
                                         (y + dy) % BOARD.shape[1])


def next_state(cell):
    """
    Infer next state of given cell.

    """

    count = count_neighbors_alive(cell)
    if is_alive(cell):
        if count < 2: return 0  # die of loneliness
        elif count > 3: return 0  # death by over-population
        else: return 1  # just the right number of buddies to roll
    else:
        if count == 3: return 1  # deadman, rearise and walk tall
        else: return 0  # stay very dead


def display():
    """
    Display state of game (of life)

    """

    for i in xrange(BOARD.shape[0]):
        row = ""
        for j in xrange(BOARD.shape[1]):
            row += [DEAD_CHR, LIVE_CHR][BOARD[i, j]]
        print row


def evolve(n_iter=-1, delay=0., n_iter_before_sleep=0):
    """
    The main loop.

    Parameters
    ----------
    n_iter: int, optional (default -1)
        Number of iterations to run. A negative value means "run forever".

    delay: float, optional (default 0)
        number of seconds to sleep between consecutive iterations.

    """

    global BOARD

    it = n_iter
    while it:
        display()
        backup = np.zeros_like(BOARD)  # backup current state
        for i in xrange(BOARD.shape[0]):
            for j in xrange(BOARD.shape[1]): backup[i, j] = next_state((i, j))
        BOARD = backup
        if delay > 0 and n_iter - it > n_iter_before_sleep: time.sleep(delay)
        it -= 1


if __name__ == "__main__":
    # make board
    motive_size = BOARD.shape[0] // 2, BOARD.shape[1] // 2
    motive = np.zeros(motive_size, dtype=np.uint8)
    motive[np.random.randn(*motive_size) > .7] = 1
    BOARD = np.hstack((motive, motive[:, ::-1]))
    BOARD = np.vstack((BOARD, BOARD[::-1, :]))

    # fire main loop
    evolve()
