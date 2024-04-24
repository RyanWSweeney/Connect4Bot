import time

import numpy as np
import random

import pandas as pd
from matplotlib import pyplot as plt

from Position import Position
from Solver import Solver


def print_mask(self):
    for row in range(Position.HEIGHT + 1):  # Include overflow bit row
        print(' '.join('1' if self & (1 << (row + col * (Position.HEIGHT + 1))) else '0'
                       for col in range(Position.WIDTH)))
    print()  # Print a newline for better readability

def visualize(board):
    board_array = np.array(board)
    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(board_array.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(board_array.shape[0]) + 0.5, minor=False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xlim(0, board_array.shape[1])
    ax.set_ylim(0, board_array.shape[0])
    ax.set_aspect('equal', 'box')

    # Draw blue background
    for i in range(Position.HEIGHT):
        for j in range(Position.WIDTH):
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor='blue', edgecolor='blue'))

    # Draw circles for tokens
    for y in range(board_array.shape[0]):
        for x in range(board_array.shape[1]):
            color = 'red' if board_array[y, x] == 1 else 'yellow' if board_array[y, x] == -1 else 'white'
            circle = plt.Circle((x + 0.5, y + 0.5), 0.4, color=color, ec='black')
            ax.add_artist(circle)

    plt.show()


def simulate_bulk_games(solver, num_games):
    results = []
    #get the minimum and maximum number of moves from user
    min_moves = int(input("Enter the minimum number of moves: "))
    max_moves = int(input("Enter the maximum number of moves: "))
    for move_count in range(min_moves, max_moves + 1):
        move_runtimes = []
        move_nodes = []
        for _ in range(num_games):
            position = Position()
            moves = ""
            while position.nb_moves() < move_count:
                move = np.random.randint(1, Position.WIDTH + 1)
                if position.play(str(move)) != 1 or position.can_win_next():
                    position = Position()  # Reset if move is invalid or game ends prematurely
                    moves = ""
                else:
                    moves += str(move)

            start_time = time.time()
            solver.reset()
            solver.solve(position, weak=False)
            elapsed_time = time.time() - start_time

            move_runtimes.append(elapsed_time)
            move_nodes.append(solver.node_count)

        results.append({
            'move_count': move_count,
            'avg_runtime': np.mean(move_runtimes),
            'avg_nodes': np.mean(move_nodes)
        })

    return results


def plot_and_export_results(results):
    df = pd.DataFrame(results)

    # Plotting Runtimes
    plt.figure(figsize=(10, 6))
    plt.plot(df['move_count'], df['avg_runtime'], marker='o', linestyle='-')
    plt.title('Average Runtime by Move Count')
    plt.xlabel('Move Count')
    plt.ylabel('Average Runtime (seconds)')
    plt.grid(True)
    plt.show()

    # Plotting Nodes Explored
    plt.figure(figsize=(10, 6))
    plt.plot(df['move_count'], df['avg_nodes'], marker='o', color='red', linestyle='-')
    plt.title('Average Nodes Explored by Move Count')
    plt.xlabel('Move Count')
    plt.ylabel('Average Nodes Explored')
    plt.grid(True)
    plt.show()

    # Exporting to CSV
    df.to_csv('bulk_simulation_results.csv', index=False)
    print("Results exported to 'bulk_simulation_results.csv'.")


def manual_game_entry(solver):
    moves = input("Enter the game moves (1-7 for each column): ")
    position = Position()
    if position.play(moves) != len(moves):
        print("Invalid move sequence!")
    else:
        #print the overall bitmask of the board
        print(f"Overall bitmask: {bin(position.current_position)}")
        #print board state
        print("Current board state:")
        print(position.board_to_array())


        print("Bottom Mask:")
        print_mask(Position.bottom_mask)

        print("Board Mask:")
        print_mask(Position.board_mask)
        # Evaluate and print scores for each possible move
        best_move = None
        best_score = -float('inf')
        print("Scores for each column:")
        for col in range(1, Position.WIDTH + 1):  # Assuming columns are 1-indexed
            if position.can_play(col - 1):  # Convert to 0-indexed internally
                test_position = Position()
                test_position.current_position = position.current_position
                test_position.mask = position.mask
                test_position.playCol(col - 1)  # Play in the column

                score = solver.solve(test_position, weak=False)
                print(f"Column {col}: {score}")

                if score > best_score:
                    best_score = score
                    best_move = col
            else:
                print(f"Column {col}: Column is full")

        if best_move is not None:
            print(f"The AI would choose column {best_move} with a score of {best_score}")
        else:
            print("No valid moves available.")


# Ensure that Position, Solver, and other necessary dependencies are properly implemented and tested


def interactive_play(solver):
    position = Position()
    while position.nb_moves() < Position.WIDTH * Position.HEIGHT and not position.can_win_next():
        user_move = int(input(f"Enter your move (1-{Position.WIDTH}): ")) - 1
        if not position.can_play(user_move):
            print("Invalid move, try again.")
            continue
        position.playCol(user_move)
        if position.can_win_next():
            print("Congratulations, you won!")
            break
        print("Solver is thinking...")
        score = solver.solve(position, weak=False)
        print(f"Solver recommends move with score: {score}")


def main():
    solver = Solver()
    print("Welcome to Connect Four simulator!")
    print("Choose an option:")
    print("1. Simulate bulk games")
    print("2. Enter game moves manually")
    print("3. Play interactively")
    choice = input("Enter your choice: ")
    if choice == '1':
        num_games = int(input("Enter the number of games to simulate: "))
        results = simulate_bulk_games(solver, num_games)
        plot_and_export_results(results)
    elif choice == '2':
        manual_game_entry(solver)
    elif choice == '3':
        interactive_play(solver)
    else:
        print("Invalid choice, exiting...")

if __name__ == "__main__":
    main()
