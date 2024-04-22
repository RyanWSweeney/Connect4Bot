import numpy as np
import matplotlib.pyplot as plt
import random
import time
import math
import sys

from TranspositionTable import TranspositionTable

sys.setrecursionlimit(100000)


class Position:
    WIDTH = 7
    HEIGHT = 6
    HEIGHT_PLUS_ONE = HEIGHT + 1

    def __init__(self):
        self.current_position = 0
        self.mask = 0
        self.moves = 0
        self.column_order = self.initialize_column_order()
        self.move_sequence = []  # List to track the sequence of played columns

    def initialize_column_order(self):
        # Generate column order prioritizing center columns
        order = list(range(self.WIDTH))
        order.sort(key=lambda x: abs(x - self.WIDTH // 2))
        return order

    @staticmethod
    def top_mask(col):
        return (1 << (Position.HEIGHT - 1)) << col * Position.HEIGHT_PLUS_ONE

    @staticmethod
    def bottom_mask(col):
        return 1 << col * Position.HEIGHT_PLUS_ONE

    @staticmethod
    def column_mask(col):
        return ((1 << Position.HEIGHT) - 1) << col * Position.HEIGHT_PLUS_ONE

    def can_play(self, col):
        return (self.mask & self.top_mask(col)) == 0

    def play(self, col):
        if not self.can_play(col):
            raise ValueError("Column is full or invalid move")
        self.current_position ^= self.mask
        self.mask |= self.mask + self.bottom_mask(col)
        self.moves += 1
        self.move_sequence.append(col + 1)  # 1-based index

    def is_winning_move(self, col):
        pos = self.current_position | ((self.mask + self.bottom_mask(col)) & self.column_mask(col))
        return self.alignment(pos)

    def is_terminal(self):
        """Check if the current position is a game-ending position."""
        # Assuming that any winning move would end the game
        if any(self.is_winning_move(col) for col in range(self.WIDTH) if self.can_play(col)):
            return True
        # Check if the board is full
        if self.nb_moves() == self.WIDTH * self.HEIGHT:
            return True
        return False

    def evaluate(self):
        """Evaluate the position; must be called only on terminal positions."""
        # If the board is full and no winner, it's a draw
        if self.nb_moves() == self.WIDTH * self.HEIGHT:
            return 0  # Draw score
        # Check which player has won and return appropriate score
        for col in range(self.WIDTH):
            if self.can_play(col) and self.is_winning_move(col):
                if self.current_position & (1 << (self.bottom_mask(col) - 1)):
                    return 1  # Current player wins
                else:
                    return -1  # Opponent wins
        return 0  # This should never be reached unless called non-terminally

    @staticmethod
    def alignment(pos):
        # Horizontal check
        m = pos & (pos >> Position.HEIGHT_PLUS_ONE)
        if m & (m >> (2 * Position.HEIGHT_PLUS_ONE)):
            return True

        # Diagonal checks
        m = pos & (pos >> Position.HEIGHT)
        if m & (m >> (2 * Position.HEIGHT)):
            return True

        m = pos & (pos >> (Position.HEIGHT + 2))
        if m & (m >> (2 * (Position.HEIGHT + 2))):
            return True

        # Vertical check
        m = pos & (pos >> 1)
        if m & (m >> 2):
            return True

        return False

    def nb_moves(self):
        return self.moves

    def clone(self):
        """Create a deep copy of this Position object."""
        new_position = Position()
        new_position.current_position = self.current_position
        new_position.mask = self.mask
        new_position.moves = self.moves
        new_position.column_order = self.column_order[:]  # Copy the list if it might change
        new_position.move_sequence = self.move_sequence[:]  # Ensure a deep copy of the move sequence
        return new_position

    def key(self):
        # Generating a unique key for the current position
        # Assuming `current_position` and `mask` can serve as a unique identifier
        return self.current_position + (self.mask << 28)  # Simple unique key generation

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

    def print_move_sequence(self):
        """Prints the sequence of columns played so far."""
        print("Move sequence:", ' -> '.join(map(str, self.move_sequence)))


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


def create_random_position(position, move_count):
    for _ in range(move_count):
        possible_moves = [col for col in range(Position.WIDTH) if position.can_play(col)]
        if not possible_moves:
            break
        move = random.choice(possible_moves)
        position.play(move)
        if position.is_winning_move(move):  # End early if a win is detected
            break


def negamax(position, alpha, beta, trans_table):
    # Check transposition table first
    tt_entry = trans_table.get(position.key())
    if tt_entry:
        # Assuming tt_entry is a score already adjusted for minimax value
        return tt_entry

    # Terminal node check (draw or win)
    if position.is_terminal():
        return position.evaluate()

    max_value = -float('inf')
    for col in range(position.WIDTH):
        if position.can_play(col):
            # Create new position by playing the move
            new_position = position.clone()
            new_position.play(col)

            # Immediate win check
            if new_position.is_winning_move(col):
                score = (Position.WIDTH * Position.HEIGHT + 1 - new_position.nb_moves()) // 2
                trans_table.put(new_position.key(), score)
                return score

            # Recursive negamax call
            value = -negamax(new_position, -beta, -alpha, trans_table)
            max_value = max(max_value, value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break

    # Store the computed value in the transposition table before returning
    trans_table.put(position.key(), max_value)
    return max_value


def iterative_deepening(position, max_depth):
    trans_table = TranspositionTable()
    best_score = None
    for depth in range(1, max_depth + 1):
        best_score = negamax(position, -float('inf'), float('inf'), trans_table)
        print(f"Depth {depth}: Best score {best_score}")
    return best_score


if __name__ == "__main__":
    # Properly initialize the transposition table with a specified size
    entry_size_bytes = 50
    entries = (64 * 1024 * 1024) // entry_size_bytes  # 64 MB divided by the size of each entry
    trans_table = TranspositionTable(size=entries)

    position = Position()
    create_random_position(position, random.randint(0, Position.WIDTH * Position.HEIGHT))

    # Visualize the board state
    visualize(position.board_state())
    position.print_move_sequence()

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
