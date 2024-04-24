import tkinter as tk
from tkinter import messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class GameState:
    def __init__(self, width=7, height=6):
        self.width = width
        self.height = height
        self.moves = []  # List to store column numbers as moves
        self.board = [[0] * width for _ in range(height)]  # 0 for empty, 1 for player 1, -1 for player 2

    def make_move(self, col):
        # Add move to the list
        if len([m for m in self.moves if m == col]) < self.height:
            self.moves.append(col)
            return True
        return False

    def to_string(self):
        # Convert moves list to string format
        return ''.join(str(move + 1) for move in self.moves)  # +1 because columns are 1-based in strings

    def can_play(self, col):
        # Check if a move can be played in the column
        return self.moves.count(col) < self.height

    def board_to_array(self):
        # Create a board array for display
        board = [[0] * self.width for _ in range(self.height)]
        for idx, move in enumerate(self.moves):
            row = self.moves[:idx].count(move)
            board[self.height - 1 - row][move] = 1 if idx % 2 == 0 else -1
        return board


class Connect4GUI:
    def __init__(self, master, solver, width=7, height=6):
        self.master = master
        self.solver = solver
        self.width = width
        self.height = height
        self.position = GameState(width, height)  # Use GameState instead
        self.master.title("Connect 4")

        # Setup the Matplotlib Figure and Axes
        self.fig, self.ax = plt.subplots(figsize=(7, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Labels for move scores
        self.score_labels = [tk.Label(master, text="Score: -", font=("Arial", 10)) for _ in range(self.width)]
        for label in self.score_labels:
            label.pack(side=tk.LEFT)

        # Buttons for player moves
        self.buttons = [tk.Button(master, text=f"Col {i+1}", command=lambda i=i: self.make_move(i))
                        for i in range(self.width)]
        for button in self.buttons:
            button.pack(side=tk.LEFT)

        # Button to trigger AI move
        self.ai_button = tk.Button(master, text="Perform AI Move", command=self.ai_move)
        self.ai_button.pack(side=tk.BOTTOM)

        self.draw_board()

    def make_move(self, col):
        if not self.position.can_play(col):
            messagebox.showerror("Invalid move", "Column is full!")
            return
        self.position.make_move(col)
        self.draw_board()
        self.update_move_scores()

    def update_move_scores(self):
        scores = []
        for col in range(self.width):
            if self.position.can_play(col) and (0 == 1):
                test_position = GameState()
                test_position.moves = self.position.moves.copy()
                test_position.make_move(col)
                score = self.solver.solve(test_position, weak=False)
                scores.append(score)
            else:
                scores.append('-')
        for i, score in enumerate(scores):
            self.score_labels[i].config(text=f"Score: {score}")



    def draw_board(self):
        self.ax.clear()
        self.ax.set_xticks(np.arange(self.width) + 0.5, minor=False)
        self.ax.set_yticks(np.arange(self.height) + 0.5, minor=False)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        self.ax.grid(which='both', color='black', linestyle='-', linewidth=2)
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_aspect('equal', 'box')
        self.ax.set_facecolor('blue')

        board = self.position.board_to_array()
        for x in range(self.width):
            for y in range(self.height):
                token = board[self.height - y - 1][x]
                color = 'red' if token == 1 else 'yellow' if token == -1 else 'white'
                self.ax.add_patch(plt.Circle((x + 0.5, self.height - y - 0.5), 0.4, color=color, ec='black'))
        #flip by y
        self.canvas.draw()

    def ai_move(self):
        best_move, best_score = None, -float('inf')
        # Iterate over each column to simulate the move and evaluate it using the solver
        for col in range(self.width):
            if self.position.can_play(col):
                # Simulate the move
                test_position = GameState(self.width, self.height)
                test_position.moves = self.position.moves.copy()  # Copy current moves
                test_position.make_move(col)

                # Convert the game state to the input string format expected by the solver
                # game_state_string = test_position.to_string()

                # Get the score from the solver
                score = self.solver.solve(test_position, weak=False)
                if score is not None and score > best_score:
                    best_score = score
                    best_move = col

        if best_move is not None:
            self.position.make_move(best_move)
            self.draw_board()
            self.update_move_scores()

            # Check for end of game
            if self.is_game_over():
                self.end_game()
        else:
            messagebox.showinfo("Move", "AI has no moves left.")

    def is_game_over(self):
        # Check if the game has ended
        return len(self.position.moves) == self.width * self.height

    def end_game(self):
        # Display the game result
        messagebox.showinfo("Game Over", "The game is a draw.")
        self.master.quit()