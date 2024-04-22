import random
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import matplotlib.pyplot as plt

from TranspositionTable import TranspositionTable
from Position import Position, negamax

# Assume 'Position' and 'negamax' have already been defined and imported.

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

def test_solver(move_counts):
    results = []
    for move_count in move_counts:
        position = create_specific_position(move_count)
        entry_size_bytes = 50
        entries = (64 * 1024 * 1024) // entry_size_bytes  # 64 MB divided by the size of each entry
        trans_table = TranspositionTable(size=entries)

        start_time = time.time()
        score = negamax(position, -float('inf'), float('inf'), trans_table)
        end_time = time.time()

        elapsed_time = end_time - start_time
        node_count = position.nb_moves()  # This should be changed to actual node count logic
        nodes_explored = position.nb_nodes()
        nodes_per_second = node_count / elapsed_time if elapsed_time > 0 else 0

        results.append((move_count, node_count, elapsed_time, nodes_per_second, nodes_explored))

        print(f"Test for {move_count} moves: Score = {score}, Nodes = {node_count}, Time = {elapsed_time:.2f} s, Nodes/s = {nodes_per_second:.2f}, TotalNodes = {nodes_explored}")

    return results

def plot_results(results):
    move_counts, node_counts, times, nodes_per_seconds = zip(*results)

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Number of Moves Played')
    ax1.set_ylabel('Nodes Explored', color=color)
    ax1.plot(move_counts, node_counts, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Time (seconds)', color=color)  # We already handled the x-label with ax1
    ax2.plot(move_counts, times, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # Otherwise the right y-label is slightly clipped
    plt.title('Performance Metrics of Connect 4 Solver')
    plt.show()


def test_solver(move_count):
    position = create_specific_position(move_count)
    trans_table = TranspositionTable(size=8388608)
    start_time = time.time()
    score = negamax(position, -float('inf'), float('inf'), trans_table)
    end_time = time.time()
    elapsed_time = end_time - start_time
    nodes_per_second = position.node_count / elapsed_time if elapsed_time > 0 else 0
    return move_count, position.node_count, elapsed_time, nodes_per_second

def run_tests(move_counts):
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(test_solver, mc) for mc in move_counts]
        for future in futures:
            result = future.result()
            print(f"Test for {result[0]} moves: Nodes = {result[1]}, Time = {result[2]:.2f} s, Nodes/s = {result[3]:.2f}, NodesExplored = {result[4]}")
            results.append(result)
    return results

def plot_results(results):
    move_counts, node_counts, times, nodes_per_seconds = zip(*results)
    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('Number of Moves Played')
    ax1.set_ylabel('Nodes Explored', color=color)
    ax1.plot(move_counts, node_counts, 'o-', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Time (seconds)', color=color)
    ax2.plot(move_counts, times, 's-', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()
    plt.title('Performance Metrics of Connect 4 Solver')
    plt.show()

if __name__ == "__main__":
    move_counts = [19,20,21,22,23,24]  # Adjust this as needed
    results = run_tests(move_counts)
    plot_results(results)
