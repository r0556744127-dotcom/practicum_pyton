import sys
from PieceRules import PieceRules
class MappBoard:
    """מבנה הנתונים הסטטי של הלוח - ניהול המטריצה בלבד."""
    def __init__(self):
        self._matrix = []
        self._expected_width = None

    def add_row(self, tokens: list) -> None:
        for token in tokens:
            if not PieceRules.is_valid_token(token):
                print("ERROR UNKNOWN_TOKEN")
                sys.exit(0)

        current_width = len(tokens)
        if self._expected_width is None:
            self._expected_width = current_width
        elif current_width != self._expected_width:
            print("ERROR ROW_WIDTH_MISMATCH")
            sys.exit(0)

        self._matrix.append(tokens)

    def get_dimensions(self):
        return len(self._matrix), self._expected_width

    def get_piece_at(self, row: int, col: int) -> str:
        return self._matrix[row][col]

    def set_piece_at(self, row: int, col: int, piece_token: str) -> None:
        self._matrix[row][col] = piece_token

    def get_raw_matrix(self):
        # מחזיר העתק של המטריצה לצורך יצירת Snapshot
        return [row[:] for row in self._matrix]


