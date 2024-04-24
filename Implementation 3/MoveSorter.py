class MoveSorter:
    def __init__(self, width):
        self.entries = []
        self.width = width  # This will replace Position::WIDTH

    def add(self, move, score):
        # Insertion sort to maintain order as in the original C++ code
        from bisect import insort_left
        insort_left(self.entries, (score, move), key=lambda x: -x[0])

    def get_next(self):
        if self.entries:
            return self.entries.pop(0)[1]
        return 0

    def reset(self):
        self.entries = []
