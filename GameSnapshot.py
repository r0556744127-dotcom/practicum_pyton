class GameSnapshot:
    """צילום מצב קפוא (Immutable) המועבר ל-Render."""
    def __init__(self, matrix, clock_ms):
        self.matrix = matrix
        self.clock_ms = clock_ms