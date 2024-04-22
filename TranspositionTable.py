class TranspositionTable:
    def __init__(self, size):
        self.size = size
        self.table = [None] * size  # Use None to indicate empty entries

    def put(self, key, value):
        index = key % self.size
        self.table[index] = (key, value)

    def get(self, key):
        index = key % self.size
        entry = self.table[index]
        if entry is not None and entry[0] == key:
            return entry[1]
        return None  # Return None to clearly indicate no data found