import numpy as np


class Position:
    WIDTH = 7
    HEIGHT = 6
    MIN_SCORE = -(WIDTH * HEIGHT) // 2 + 3
    MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3

    bottom_mask = sum(1 << (7 * i) for i in range(7))
    board_mask = (1 << 6) - 1

    def __init__(self):
        self.current_position = 0
        self.mask = 0
        self.moves = 0

    def play(self, move):
        if isinstance(move, int):  # Handling bitboard move directly
            self.current_position ^= self.mask
            self.mask |= move
            self.moves += 1
        elif isinstance(move, str):  # Handling string sequence of moves
            return self.play_sequence(move)

    def play_sequence(self, moves):
        for i, char in enumerate(moves):
            col = int(char) - 1
            if not self.can_play(col):
                return i
            if self.is_winning_move(col):
                return i
            self.playCol(col)
        return len(moves)

    def can_play(self, col):
        top_cell = 1 << ((self.HEIGHT - 1) + col * (self.HEIGHT + 1))
        return (self.mask & top_cell) == 0

    def playCol(self, col):
        move = (self.mask + self.bottom_mask_col(col)) & self.column_mask(col)
        self.play(move)

    def is_winning_move(self, col):
        move = (self.mask + self.bottom_mask_col(col)) & self.column_mask(col)
        return bool(self.winning_position() & move)

    def can_win_next(self):
        #if any of the winning positions is a subset of the current position, then the current player can win in the next move
        return bool(self.winning_position() & self.current_position)

    def winning_position(self):
        return self.compute_winning_position(self.current_position, self.mask)

    def compute_winning_position(self, position, mask):
        vertical = (position << 1) & (position << 2) & (position << 3)
        horizontal = (position << (self.HEIGHT + 1)) & (position << 2 * (self.HEIGHT + 1)) & (position << 3 * (self.HEIGHT + 1))
        diag1 = (position << self.HEIGHT) & (position << 2 * self.HEIGHT) & (position << 3 * self.HEIGHT)
        diag2 = (position << (self.HEIGHT + 2)) & (position << 2 * (self.HEIGHT + 2)) & (position << 3 * (self.HEIGHT + 2))
        return vertical | horizontal | diag1 | diag2

    @staticmethod
    def bottom_mask_col(col):
        return 1 << (col * (Position.HEIGHT + 1))

    @staticmethod
    def column_mask(col):
        return ((1 << Position.HEIGHT) - 1) << (col * (Position.HEIGHT + 1))

    def possible(self):
        return (self.mask + Position.bottom_mask) & Position.board_mask

    def opponent_winning_position(self):
        opponent_position = self.mask & ~self.current_position
        return self.compute_winning_position(opponent_position, self.mask)

    def nb_moves(self):
        return self.moves

    def board_to_array(self):
        board = np.zeros((self.HEIGHT, self.WIDTH), dtype=int)
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                if self.current_position & (1 << (y + x * (self.HEIGHT + 1))):
                    board[y, x] = 1
                elif self.mask & (1 << (y + x * (self.HEIGHT + 1))):
                    board[y, x] = -1
        return board

    def possible_non_losing_moves(self):
        return self.possible() & ~(self.opponent_winning_position())

    def key(self):
        #add mask to the key to differentiate between positions with the same current_position
        return self.current_position + self.mask