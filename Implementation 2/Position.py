import random
import time

import numpy as np
from matplotlib import pyplot as plt

from TranspositionTable import TranspositionTable


class MoveSorter:
    def __init__(self):
        self.entries = []  # List to store moves and their scores

    def add(self, move, score):
        self.entries.append((score, move))
        self.entries.sort(reverse=True, key=lambda x: x[0])  # Sort by score in descending order

    def getNext(self):
        if self.entries:
            return self.entries.pop(0)[1]
        return 0



class Position:
    WIDTH = 7
    HEIGHT = 6
    HEIGHT_PLUS_ONE = HEIGHT + 1
    BOARD_MASK = ((1 << (HEIGHT_PLUS_ONE * WIDTH)) - 1)
    MIN_SCORE = -(WIDTH * HEIGHT) // 2 + 3
    MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3

    def __init__(self):
        self.move_sequence = None
        self.current_position = 0  # Bitboard for current player
        self.mask = 0  # Bitboard for all discs
        self.moves = 0  # Number of moves played
        self.node_count = 0  # Initialize node count

    def increment_node_count(self):
        self.node_count += 1

    def play(self, col):
        """ Play a move in the given column. """
        if not self.can_play(col):
            raise ValueError("Column is full or move is illegal")
        self.current_position ^= self.mask
        self.mask |= self.mask + self.bottom_mask(col)
        self.moves += 1

    def can_play(self, col):
        """ Check if a move can be played in the given column. """
        return (self.mask & self.top_mask(col)) == 0

    def is_winning_move(self, col):
        """ Check if playing in the given column results in a win. """
        pos = self.current_position | (self.mask + self.bottom_mask(col)) & self.column_mask(col)
        return self.alignment(pos)

    @staticmethod
    def top_mask(col):
        return 1 << (Position.HEIGHT - 1) << col * Position.HEIGHT_PLUS_ONE

    @staticmethod
    def bottom_mask(col):
        return 1 << col * Position.HEIGHT_PLUS_ONE

    @staticmethod
    def column_mask(col):
        return ((1 << Position.HEIGHT) - 1) << col * Position.HEIGHT_PLUS_ONE

    @staticmethod
    def alignment(pos):
        """ Check for any kind of four alignment. """
        # Horizontal, vertical, diagonal checks
        m = pos & (pos >> Position.HEIGHT_PLUS_ONE)
        if m & (m >> (2 * Position.HEIGHT_PLUS_ONE)):
            return True
        m = pos & (pos >> Position.HEIGHT)
        if m & (m >> (2 * Position.HEIGHT)):
            return True
        m = pos & (pos >> (Position.HEIGHT + 2))
        if m & (m >> (2 * (Position.HEIGHT + 2))):
            return True
        m = pos & (pos >> 1)
        if m & (m >> 2):
            return True
        return False

    def possible(self):
        """ Returns a bitmask of all possible moves (where the top row is not filled). """
        return (self.mask + self.bottom_mask_all()) & self.BOARD_MASK

    def bottom_mask_all(self):
        """ Returns a mask with the lowest free position set to 1 in each column. """
        return (1 << Position.HEIGHT_PLUS_ONE) - 1

    def opponent_winning_position(self):
        """ Calculate potential winning positions for the opponent. """
        return self.compute_winning_position(self.current_position ^ self.mask, self.mask)

    @staticmethod
    def compute_winning_position(position, mask):
        """ Compute all winning positions given the current position and mask. """
        # vertical, horizontal, diagonal checks are performed here using bitwise operations
        vertical = (position << 1) & (position << 2) & (position << 3)
        horizontal = Position.compute_horizontal_wins(position)
        diag1 = Position.compute_diagonal1_wins(position)
        diag2 = Position.compute_diagonal2_wins(position)
        return (vertical | horizontal | diag1 | diag2) & (Position.BOARD_MASK ^ mask)

    @staticmethod
    def compute_horizontal_wins(position):
        p = (position << Position.HEIGHT_PLUS_ONE) & (position << 2 * Position.HEIGHT_PLUS_ONE)
        return (p & (position << 3 * Position.HEIGHT_PLUS_ONE)) | (p & (position >> Position.HEIGHT_PLUS_ONE))

    @staticmethod
    def compute_diagonal1_wins(position):
        p = (position << Position.HEIGHT) & (position << 2 * Position.HEIGHT)
        return (p & (position << 3 * Position.HEIGHT)) | (p & (position >> Position.HEIGHT))

    @staticmethod
    def compute_diagonal2_wins(position):
        p = (position << (Position.HEIGHT + 2)) & (position << 2 * (Position.HEIGHT + 2))
        return (p & (position << 3 * (Position.HEIGHT + 2))) | (p & (position >> (Position.HEIGHT + 2)))

    @staticmethod
    def bit_to_col(bit):
        """ Helper method to convert a bit position to a column index. """
        return (bit.bit_length() - 1) // Position.HEIGHT_PLUS_ONE

    def possibleNonLosingMoves(self):
        """ Return a bitmap of all the possible next moves that do not lose in one turn. """
        possible_mask = self.possible()
        opponent_win = self.opponent_winning_position()
        forced_moves = possible_mask & opponent_win
        if forced_moves:
            if forced_moves & (forced_moves - 1):  # More than one forced move
                return 0  # Opponent has multiple winning moves; can't block all.
            else:
                possible_mask = forced_moves  # Only one forced move; must play it.
        return possible_mask & ~(opponent_win >> 1)  # Avoid playing under opponent winning spot.

    def key(self):
        """ Generate a unique key for the current position which is used for the transposition table. """
        return self.current_position + self.mask

    def popcount(m):
        return m.bit_count()
    def clone(self):
        new_pos = Position()
        new_pos.current_position = self.current_position
        new_pos.mask = self.mask
        new_pos.moves = self.moves
        return new_pos

    def nb_moves(self):
        return self.moves

    def nb_nodes(self):
        return self.node_count

    def board_state(self):
        board = [[0] * self.WIDTH for _ in range(self.HEIGHT)]
        for col in range(self.WIDTH):
            for row in range(self.HEIGHT):
                pos = row + col * self.HEIGHT_PLUS_ONE
                if self.mask & (1 << pos):
                    if self.current_position & (1 << pos):
                        board[row][col] = 1
                    else:
                        board[row][col] = -1
        return board


def create_random_position(position, move_count):
    for _ in range(move_count):
        possible_moves = [col for col in range(Position.WIDTH) if position.can_play(col)]
        if not possible_moves:
            break
        move = random.choice(possible_moves)
        position.play(move)
        if position.is_winning_move(move):  # End early if a win is detected
            break

def create_specific_position(move_count):
    position = Position()
    while position.nb_moves() < move_count:
        possible_moves = [col for col in range(Position.WIDTH) if position.can_play(col)]
        if not possible_moves:
            break
        move = random.choice(possible_moves)
        position.play(move)
        if position.is_winning_move(move):
            position = Position()  # Reset if a win is detected prematurely
    return position

def visualize(board):
    board_array = np.array(board)
    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(board_array.shape[1]) + 0.5, minor=False)  # Set ticks between cells
    ax.set_yticks(np.arange(board_array.shape[0]) + 0.5, minor=False)  # Set ticks between cells
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xlim(0, board_array.shape[1])
    ax.set_ylim(0, board_array.shape[0])
    ax.set_aspect('equal', 'box')

    # Blue background
    for i in range(Position.HEIGHT):
        for j in range(Position.WIDTH):
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor='blue', edgecolor='blue'))

    # Add circles for tokens
    for y in range(board_array.shape[0]):
        for x in range(board_array.shape[1]):
            if board_array[y, x] == 1:
                circle = plt.Circle((x + 0.5, y + 0.5), 0.4, color='red', ec='black')
            elif board_array[y, x] == -1:
                circle = plt.Circle((x + 0.5, y + 0.5), 0.4, color='yellow', ec='black')
            else:
                circle = plt.Circle((x + 0.5, y + 0.5), 0.4, color='white', ec='black')
            ax.add_artist(circle)

    plt.show()


def negamax(position, alpha, beta, trans_table):
    position.increment_node_count()
    if position.moves == Position.WIDTH * Position.HEIGHT:
        return 0  # Draw

    for col in range(Position.WIDTH):
        if position.can_play(col) and position.is_winning_move(col):
            return (Position.WIDTH * Position.HEIGHT + 1 - position.moves) // 2

    moves = position.possibleNonLosingMoves()
    if moves == 0:
        return -Position.MAX_SCORE  # No viable moves left, loss inevitable

    max_eval = float('-inf')
    while moves:
        move = moves & -moves  # Get the lowest bit set
        col = Position.bit_to_col(move)
        if position.can_play(col):
            new_position = position.clone()
            new_position.play(col)
            eval = -negamax(new_position, -beta, -alpha, trans_table)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break
        moves &= moves - 1  # Remove the lowest bit set

    return max_eval


if __name__ == "__main__":
    # Properly initialize the transposition table with a specified size
    entry_size_bytes = 50
    entries = (64 * 1024 * 1024) // entry_size_bytes  # 64 MB divided by the size of each entry
    trans_table = TranspositionTable(size=entries)

    position = create_specific_position(random.randint(20, 40))

    # Visualize the board state
    visualize(position.board_state())
    # position.print_move_sequence()

    # Start timing the negamax function
    start_time = time.time()

    # Correctly pass the transposition table instance and include the depth parameter
    score = negamax(position, -float('inf'), float('inf'), trans_table)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time

    # Print the results
    print(f"Evaluated score: {score}")
    print(f"Number of moves: {position.nb_moves()}")
    print(f"Elapsed time: {elapsed_time:.6f} seconds")