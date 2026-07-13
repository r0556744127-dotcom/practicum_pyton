from PieceRules import PieceRules
from MappBoard import MappBoard

class RuleEngine:

    CELL_SIZE = 100

    def __init__(self, board: MappBoard):
        self.board = board

    def is_valid_move(self, piece, src_row, src_col, dst_row, dst_col, target_piece):
        # העברה לפונקציה הסטטית של PieceRules
        return PieceRules.is_valid_move(piece, src_row, src_col, dst_row, dst_col, target_piece)

    def convert_pixel_to_cell(self, x, y):
        rows, cols = self.board.get_dimensions()

        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if 0 <= row < rows and 0 <= col < cols:
            return row, col

        return None

    def is_friendly(self, cell_a, cell_b):
        if cell_a is None or cell_b is None:
            return False

        p1 = self.board.get_piece_at(cell_a[0], cell_a[1])
        p2 = self.board.get_piece_at(cell_b[0], cell_b[1])

        if p1 == '.' or p2 == '.':
            return False

        # בודק האם האות הראשונה של התג (w או b) זהה
        return p1[0] == p2[0]

    def is_path_clear(self, src, dst):
        # הגנה מפני לחיצה על אותו תא שמייצרת צעד 0 ולולאה אינסופית
        if src == dst:
            return False

        src_row, src_col = src
        dst_row, dst_col = dst

        piece = self.board.get_piece_at(src_row, src_col)

        if piece == '.':
            return False

        # פרש (N) מדלג מעל חוסמים, אין צורך לבדוק את הדרך
        if piece[1] == 'N':
            return True

        # חישוב כיוון הצעד: 1, -1 או 0
        row_step = (dst_row > src_row) - (dst_row < src_row)
        col_step = (dst_col > src_col) - (dst_col < src_col)

        row = src_row + row_step
        col = src_col + col_step

        # הלולאה רצה על כל התאים במסלול *לפני* משבצת היעד
        while (row, col) != (dst_row, dst_col):
            if self.board.get_piece_at(row, col) != '.':
                return False  # נמצא חוסם בדרך
            row += row_step
            col += col_step

        return True