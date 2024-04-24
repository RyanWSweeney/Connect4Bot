import subprocess
from Connect4GUI import Connect4GUI
import tkinter as tk


class CompiledSolverInterface:
    def __init__(self, executable_path):
        self.executable_path = executable_path

    def solve(self, position, weak=False):
        input_string = position.to_string()
        command = [self.executable_path]
        if weak:
            command.append('-w')

        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)

        # Send the input and immediately close stdin to signal end of input
        process.stdin.write(input_string + '\n')
        process.stdin.close()

        # Read the output
        output = process.stdout.read()  # Read all output at once since it's quick
        stderr = process.stderr.read()

        if stderr:
            print("Error:", stderr)

        print("Received output:", output)

        if output:
            try:
                parts = output.strip().split()
                score = int(parts[-3])
                return score
            except (IndexError, ValueError) as e:
                print("Failed to parse the expected output:", e)
                return None
        else:
            print("No valid output received from solver")
            return None


# Usage in GUI
if __name__ == "__main__":
    import struct

    print(struct.calcsize("P") * 8)

    root = tk.Tk()
    solver = CompiledSolverInterface('./Connect4Solver.exe')  # Update the path to where you move the executable
    app = Connect4GUI(root, solver)
    root.mainloop()
