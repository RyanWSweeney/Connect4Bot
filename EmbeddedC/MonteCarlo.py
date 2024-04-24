import random


class MonteCarloAgent:
    def __init__(self, num_simulations=1000):
        self.num_simulations = num_simulations

    def solve(self, game_state):
        legal_moves = [col for col in range(game_state.width) if game_state.can_play(col)]
        wins = [0] * game_state.width
        total_simulations = 0

        for move in legal_moves:
            total_wins = 0
            for _ in range(self.num_simulations):
                test_state = game_state.clone()  # Make a copy of the game state for simulation
                test_state.make_move(move)
                result = self.simulate_game(test_state)
                if result == 1:
                    total_wins += 1
                elif result == -1:
                    total_wins -= 1
            wins[move] = total_wins
            total_simulations += self.num_simulations

        probabilities = [win / total_simulations for win in wins]
        best_move = legal_moves[probabilities.index(max(probabilities))]
        return best_move

    def simulate_game(self, game_state):
        while not game_state.is_game_over():
            legal_moves = [col for col in range(game_state.width) if game_state.can_play(col)]
            move = random.choice(legal_moves)
            game_state.make_move(move)

        if game_state.is_draw():
            return 0
        elif game_state.get_winner() == 1:
            return 1
        else:
            return -1
