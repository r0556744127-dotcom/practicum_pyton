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
    def is_path_clear(self, src, dst) -> bool:
        src_row, src_col = src
        dst_row, dst_col = dst
        
        piece_token = self.board.get_piece_at(src_row, src_col)
        if piece_token == '.':
            return False
            
        piece_type = piece_token[1] # למשל 'K', 'R', 'B', 'N'
        
        # פרש (N) יכול לקפוץ מעל חוסמים - הדרך שלו תמיד נחשבת פנויה
        if piece_type == 'N':
            return True
            
        row_diff = dst_row - src_row
        col_diff = dst_col - src_col
        
        # קביעת כיוון הצעדים (1, -1 או 0)
        step_row = (row_diff > 0) - (row_diff < 0)
        step_col = (col_diff > 0) - (col_diff < 0)
        
        # בדיקה שמדובר בתנועה חוקית בקו ישר (צריח) או אלכסון (רץ)
        # (אם זו תנועה לא מוגדרת, למשל לא ישר ולא אלכסון, נחזיר False)
        if step_row != 0 and step_col != 0 and abs(row_diff) != abs(col_diff):
            return False
            
        curr_row = src_row + step_row
        curr_col = src_col + step_col
        
        # סריקת כל המשבצות בדרך *לפני* משבצת היעד
        while (curr_row, curr_col) != (dst_row, dst_col):
            if self.board.get_piece_at(curr_row, curr_col) != '.':
                return False # נמצא חוסם בדרך!
            curr_row += step_row
            curr_col += step_col
            
        return True
    def is_friendly(self, cell_a, cell_b) -> bool:
        if not cell_a or not cell_b:
            return False
        p1 = self.board.get_piece_at(cell_a[0], cell_a[1])
        p2 = self.board.get_piece_at(cell_b[0], cell_b[1])
        if p1 == '.' or p2 == '.':
            return False
        return p1[0] == p2[0] # בדיקת אות ראשונה של הצבע (w/b)
 