class TranspositionTable:
    def __init__(self, size=8388608):  # Size close to C++ implementation
        self.table = [None] * size

    def put(self, key, value):
        index = key % len(self.table)
        self.table[index] = (key, value)

    def get(self, key):
        index = key % len(self.table)
        entry = self.table[index]
        if entry is not None and entry[0] == key:
            return entry[1]
        return None


