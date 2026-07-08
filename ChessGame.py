from ChessBoard import ChessBoard
from Piece import Piece

class ChessGame:
    """מנהלת את מצב המשחק בזמן אמת, כולל זיהוי סיום משחק מיידי,
    איפוס ישויות נבחרות וחסימת מהלכים מאוחרים.
    """
    
    def __init__(self, board: ChessBoard):
        self._board = board
        self._selected_cell = None
        self._current_time_ms = 0
        self._pending_move = None  # מבנה: (start_row, start_col, end_row, end_col, piece_token, end_time)
        self._is_game_over = False  # דגל לסיום המשחק

    def _flush_pending_move_if_time_passed(self) -> None:
        """מממשת מהלכים שהסתיימו. אם המלך הוכרע, נועלת את המשחק ומאפסת בחירות."""
        if self._is_game_over:
            return

        if self._pending_move:
            start_row, start_col, end_row, end_col, piece_token, end_time = self._pending_move
            if self._current_time_ms >= end_time:
                # בדיקה אם יש מלך ביעד לפני הדריסה
                target_piece = self._board.get_piece_at(end_row, end_col)
                
                # עדכון הלוח פיזית
                self._board.set_piece_at(start_row, start_col, '.')
                self._board.set_piece_at(end_row, end_col, piece_token)
                
                # פינוי המהלך הממתין
                self._pending_move = None

                # אם המלך נתפס - המשחק נגמר ברגע זה
                if target_piece.lower() == 'k':
                    self._is_game_over = True
                    self._selected_cell = None  # איפוס קריטי של כל כלי שהיה מסומן

    def handle_click(self, x: int, y: int) -> None:
        # 1. סנכרון זמן נוכחי (מריץ flush אם הזמן עבר)
        self._flush_pending_move_if_time_passed()
        
        # 2. חסימת סיום משחק: אם המשחק נגמר, אין לקבל שום לחיצה חדשה
        if self._is_game_over:
            return
            
        # 3. חסימת סכסוכי תנועה: אם יש כלי בתנועה, מתעלמים מהלחיצה
        if self._pending_move is not None:
            return

        coords = self._board.convert_coordinates(x, y)
        if coords is None:
            return

        row, col = coords

        # 4. ניהול לוגיקת בחירה ותנועה
        if self._selected_cell is None:
            if not self._board.is_empty_cell(row, col):
                self._selected_cell = (row, col)
            return

        start_row, start_col = self._selected_cell
        
        # טיפול בלחיצה על כלי ידידותי (החלפת בחירה או ביטול)
        if self._board.is_friendly_piece(row, col, self._selected_cell):
            if (row, col) != (start_row, start_col):
                self._selected_cell = (row, col)
            else:
                self._selected_cell = None
            return

        # בדיקת חוקיות ושיגור המהלך
        if Piece.is_legal_move(self._board, start_row, start_col, row, col):
            piece_token = self._board.get_piece_at(start_row, start_col)
            
            # חישוב משך הזמן (1000 מילישניות לכל משבצת במסלול המשותף)
            distance_cells = max(abs(row - start_row), abs(col - start_col))
            duration = distance_cells * 1000
            end_time = self._current_time_ms + duration
            
            self._pending_move = (start_row, start_col, row, col, piece_token, end_time)
            self._selected_cell = None
        else:
            # מהלך מקדים לא חוקי - מאפסים בחירה
            self._selected_cell = None

    def handle_wait(self, ms: int) -> None:
        """מקדמת את הזמן. אם המשחק כבר נגמר, מתעלמת מהפקודה."""
        if self._is_game_over:
            return
            
        self._current_time_ms += ms
        self._flush_pending_move_if_time_passed()

    def handle_print(self) -> None:
        """מדפיסה את מצב הלוח נכון לרגע זה (כולל flush אחרון)."""
        self._flush_pending_move_if_time_passed()
        print(self._board.get_formatted_board())