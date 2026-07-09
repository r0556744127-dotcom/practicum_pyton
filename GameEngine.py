
import sys
# ייבוא הרכיבים הנחוצים מתוך הקבצים המקבילים בשורש הפרויקט
from RuleEngine import RuleEngine

class GameEngine:
    """מנוע המשחק הראשי שמנהל את הסטייט הדינמי והזמן."""
    
    # שימוש במחרוזת 'MappBoard' מונע NameError ובעיות ייבוא מעגליות
    def __init__(self, board: 'MappBoard'):
        self.board = board
        self.rule_engine = RuleEngine(board)
        self.selected_cell = None
        self.game_clock_ms = 0

    def handle_click(self, x: int, y: int) -> None:
        coords = self.rule_engine.convert_pixel_to_cell(x, y)
        if coords is None:
            return # מחוץ ללוח - מתעלמים

        row, col = coords
        current_piece = self.board.get_piece_at(row, col)

        if self.selected_cell is None:
            if current_piece != '.':
                self.selected_cell = (row, col) # בחירת כלי
        else:
            if self.rule_engine.is_friendly((row, col), self.selected_cell):
                self.selected_cell = (row, col) # החלפת בחירה
            else:
                # ביצוע תנועה חופשית (באיטרציה זו אין עדיין חוקי שחמט)
                src_row, src_col = self.selected_cell
                piece = self.board.get_piece_at(src_row, src_col)
                self.board.set_piece_at(src_row, src_col, '.')
                self.board.set_piece_at(row, col, piece)
                self.selected_cell = None

    def handle_wait(self, ms: int) -> None:
        self.game_clock_ms += ms

    # עטיפת GameSnapshot בגרשיים כדי למנוע שגיאת זיהוי
    def create_snapshot(self) -> 'GameSnapshot':
        # ייבוא מקומי רק בזמן קריאה לפונקציה כדי למנוע בעיות אתחול
        from GameSnapshot import GameSnapshot
        return GameSnapshot(self.board.get_raw_matrix(), self.game_clock_ms)