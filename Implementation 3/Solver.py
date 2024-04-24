import copy
import math
import time
from Position import Position
from MoveSorter import MoveSorter
from TranspositionTable import TranspositionTable

class Solver:
    def __init__(self, width=7, height=6):
        self.width = width
        self.height = height
        self.node_count = 0
        self.trans_table = TranspositionTable(key_size=64, value_size=64, log_size=22)  # Adjust these values based on your actual configuration
        # Initialize column order as in C++, centered and alternating
        self.column_order = [width // 2 + (1 - 2 * (i % 2)) * (i + 1) // 2 for i in range(width)]

    def reset(self):
        self.trans_table.reset()
        self.node_count = 0

    def negamax(self, P, alpha, beta):
        assert alpha < beta
        assert not P.can_win_next()

        self.node_count += 1

        possible = P.possible_non_losing_moves()
        if possible == 0:
            return -(Position.WIDTH * Position.HEIGHT - P.nb_moves()) // 2

        if P.nb_moves() >= Position.WIDTH * Position.HEIGHT - 2:
            return 0

        min_score = -(Position.WIDTH * Position.HEIGHT - 2 - P.nb_moves()) // 2
        if alpha < min_score:
            alpha = min_score
            if alpha >= beta:
                return alpha

        max_score = (Position.WIDTH * Position.HEIGHT - 1 - P.nb_moves()) // 2
        if beta > max_score:
            beta = max_score
            if alpha >= beta:
                return beta

        key = P.key()
        val = self.trans_table.get(key)
        if val:
            if val > Position.MAX_SCORE - Position.MIN_SCORE + 1:
                min_score = val + 2 * Position.MIN_SCORE - Position.MAX_SCORE - 2
                if alpha < min_score:
                    alpha = min_score
                    if alpha >= beta:
                        return alpha
            else:
                max_score = val + Position.MIN_SCORE - 1
                if beta > max_score:
                    beta = max_score
                    if alpha >= beta:
                        return beta

        moves = MoveSorter(self.width)
        for i in reversed(range(self.width)):  # Iterate from the last to first for MoveSorter
            move = possible & Position.column_mask(self.column_order[i])
            if move:
                moves.add(move, P.move_score(move))  # Adjust the move_score method accordingly

        while True:
            next_move = moves.get_next()
            if not next_move:
                break
            P2 = P.clone()  # Make sure to implement clone method in Position or use copy.deepcopy
            P2.play(next_move)
            score = -self.negamax(P2, -beta, -alpha)
            if score >= beta:
                self.trans_table.put(key, score + Position.MAX_SCORE - 2 * Position.MIN_SCORE + 2)
                return score
            if score > alpha:
                alpha = score

        self.trans_table.put(key, alpha - Position.MIN_SCORE + 1)
        return alpha

    def solve(self, P, weak=False):
        if P.can_win_next():
            return (Position.WIDTH * Position.HEIGHT + 1 - P.nb_moves()) // 2

        min_score = -(Position.WIDTH * Position.HEIGHT - P.nb_moves()) // 2
        max_score = (Position.WIDTH * Position.HEIGHT + 1 - P.nb_moves()) // 2
        if weak:
            min_score = -1
            max_score = 1

        while min_score < max_score:
            med = min_score + (max_score - min_score) // 2
            if med <= 0 and min_score // 2 < med:
                med = min_score // 2
            elif med >= 0 and max_score // 2 > med:
                med = max_score // 2
            r = self.negamax(P, med, med + 1)
            if r <= med:
                max_score = r
            else:
                min_score = r

        return min_score
