from math import ceil, log2

class TranspositionTable:
    def __init__(self, key_size, value_size, log_size):
        # key_size and value_size are included for completeness and potential future use,
        # but they don't directly affect the implementation in a dynamic language like Python.
        self.size = 2 ** ceil(log2(2 ** log_size))  # Actual size as a power of 2
        self.entries = {}

    def reset(self):
        self.entries.clear()

    def put(self, key, value):
        if value == 0:
            # Zero is used to encode missing data, hence we remove the key if value is 0
            self.entries.pop(key, None)  # Use pop for a cleaner deletion
        else:
            self.entries[key] = value

    def get(self, key):
        return self.entries.get(key, 0)
