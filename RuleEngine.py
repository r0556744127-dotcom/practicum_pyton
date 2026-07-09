import sys
from MappBoard import MappBoard
class RuleEngine:
    """מנוע אכיפת החוקים הגאומטריים והטקטיים של הלוח."""
    CELL_SIZE = 100

    def __init__(self, board: MappBoard):
        self.board = board

    def convert_pixel_to_cell(self, x: int, y: int):
        rows, cols = self.board.get_dimensions()
        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if 0 <= row < rows and 0 <= col < cols:
            return row, col
        return None

    def is_friendly(self, cell_a, cell_b) -> bool:
        if not cell_a or not cell_b:
            return False
        p1 = self.board.get_piece_at(cell_a[0], cell_a[1])
        p2 = self.board.get_piece_at(cell_b[0], cell_b[1])
        if p1 == '.' or p2 == '.':
            return False
        return p1[0] == p2[0] # בדיקת אות ראשונה של הצבע (w/b)