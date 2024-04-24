import sys
from Position import Position
from MoveSorter import MoveSorter
from Solver import Solver
import time


def main():
    solver = Solver()
    weak = '-w' in sys.argv

    # for line in sys.stdin:
    #     line = line.strip()
    #     if not line:
    #         continue
    #
    #     position = Position()
    #     if position.play(line) != len(line):
    #         sys.stderr.write(f"Invalid move in line: {line}\n")
    #     else:
    #         solver.reset()
    #         start_time = time.time()
    #         score = solver.solve(position, weak)
    #         end_time = time.time()
    #
    #         elapsed_time = (end_time - start_time) * 1e6  # convert to microseconds
    #         print(f"{line} {score} {solver.node_count} {int(elapsed_time)}")

    # After setting up the board with "443456"
    position = Position()
    position.play("123")
    print("Current board state:")
    print(position.board_to_array())  # Assuming this method prints a human-readable board

    if position.can_win_next():
        print("Win next move is possible!")
    else:
        print("No immediate win detected.")


if __name__ == "__main__":
    main()
