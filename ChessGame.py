from ChessBoard import ChessBoard
from Piece import Piece

class ChessGame:
    """מנהלת את מצב המשחק באינטראקציה מתקדמת בזמן אמת: 
    חסימת מהלכים לא חוקיים, ניהול הכאות אויב בזמן הגעה, ומניעת סכסוכי תנועה.
    """
    
    def __init__(self, board: ChessBoard):
        self._board = board
        self._selected_cell = None
        self._current_time_ms = 0
        self._pending_move = None  # מבנה: (start_row, start_col, end_row, end_col, piece_token, end_time)

    def _flush_pending_move_if_time_passed(self) -> None:
        """מבצעת את המהלך בפועל (כולל הכאת אויב ביעד) רק כשהגיע זמן ההגעה."""
        if self._pending_move:
            start_row, start_col, end_row, end_col, piece_token, end_time = self._pending_move
            if self._current_time_ms >= end_time:
                # ברגע ההגעה: מפנים את משבצת המקור, ומציבים ביעד (דורס כלי אויב אם היה שם)
                self._board.set_piece_at(start_row, start_col, '.')
                self._board.set_piece_at(end_row, end_col, piece_token)
                self._pending_move = None

    def handle_click(self, x: int, y: int) -> None:
        # 1. סנכרון זמן ראשוני
        self._flush_pending_move_if_time_passed()
        
        # 2. פתרון סכסוכי תנועה: אם כלי עדיין באמצע תנועה, מתעלמים מכל פקודת לחיצה חדשה
        if self._pending_move is not None:
            return

        coords = self._board.convert_coordinates(x, y)
        if coords is None:
            return

        row, col = coords

        # 3. שלב א': בחירת כלי ראשונית
        if self._selected_cell is None:
            if not self._board.is_empty_cell(row, col):
                self._selected_cell = (row, col)
            return

        # שלב ב': יש כבר כלי נבחר, כעת נקבע היעד
        start_row, start_col = self._selected_cell
        
        # טיפול בנחיתה על כלי ידידותי או החלפת בחירה
        if self._board.is_friendly_piece(row, col, self._selected_cell):
            # אם לחצנו על כלי ידידותי אחר, נחליף את הבחירה אליו (התנהגות מקובלת)
            if (row, col) != (start_row, start_col):
                self._selected_cell = (row, col)
            else:
                # לחיצה חוזרת על אותו כלי מבטלת את הבחירה
                self._selected_cell = None
            return

        # 4. בדיקת חוקיות המהלך (חסימת מהלכים מקדימים לא חוקיים ונחיתה לא חוקית)
        if Piece.is_legal_move(self._board, start_row, start_col, row, col):
            piece_token = self._board.get_piece_at(start_row, start_col)
            
            # חישוב המרחק והזמן (1000 מילישניות לכל תא)
            distance_cells = max(abs(row - start_row), abs(col - start_col))
            duration = distance_cells * 1000
            end_time = self._current_time_ms + duration
            
            # שיגור המהלך לתנועה בזמן אמת
            self._pending_move = (start_row, start_col, row, col, piece_token, end_time)
            self._selected_cell = None
        else:
            # מהלך מקדים לא חוקי - המנוע מאפס את הבחירה באופן עקבי ולא מבצע דבר
            self._selected_cell = None

    def handle_wait(self, ms: int) -> None:
        """מקדמת את שעון המשחק ומבצעת עדכוני תנועה והכאות בהתאם."""
        self._current_time_ms += ms
        self._flush_pending_move_if_time_passed()

    def handle_print(self) -> None:
        """מדפיסה את הלוח העדכני ביותר."""
        self._flush_pending_move_if_time_passed()
        print(self._board.get_formatted_board())