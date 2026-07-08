from ChessBoard import ChessBoard
from Piece import Piece

class ChessGame:
    """מנהלת את מצב המשחק, מניעת הסטה בזמן תנועה, ושחרור מיידי של כלים בהגעה."""
    
    def __init__(self, board: ChessBoard):
        self._board = board
        self._selected_cell = None
        self._current_time_ms = 0
        self._pending_move = None  # מבנה: (start_row, start_col, end_row, end_col, piece_token, end_time)

    def _flush_pending_move_if_time_passed(self) -> None:
        """מממשת את המהלך על הלוח ומנקה אותו אם זמן ההגעה הגיע או עבר."""
        if self._pending_move:
            start_row, start_col, end_row, end_col, piece_token, end_time = self._pending_move
            if self._current_time_ms >= end_time:
                # עדכון הלוח הפיזי
                self._board.set_piece_at(start_row, start_col, '.')
                self._board.set_piece_at(end_row, end_col, piece_token)
                # ניקוי המהלך הממתין - מאפשר תנועה מיידית מחדש ללא קירור
                self._pending_move = None

    def handle_click(self, x: int, y: int) -> None:
        # 1. קודם כל נבדוק אם מהלך קודם כבר הסתיים בזמן הנוכחי
        self._flush_pending_move_if_time_passed()
        
        # 2. בדיקה: אם הכלי עדיין בתנועה (הזמן לא עבר), מתעלמים מהלחיצה (מניעת הסטה)
        if self._pending_move is not None:
            return

        coords = self._board.convert_coordinates(x, y)
        if coords is None:
            return

        row, col = coords

        # 3. ניהול בחירה ותנועה רגילה
        if self._selected_cell is None:
            if not self._board.is_empty_cell(row, col):
                self._selected_cell = (row, col)
        else:
            start_row, start_col = self._selected_cell
            
            # החלפת בחירה בין כלים מאותו צבע
            if self._board.is_friendly_piece(row, col, self._selected_cell):
                self._selected_cell = (row, col)
                return

            # בדיקת חוקיות ושיגור מהלך
            if Piece.is_legal_move(self._board, start_row, start_col, row, col):
                piece_token = self._board.get_piece_at(start_row, start_col)
                
                # חישוב משך זמן נסיעה (1000 מילישניות לכל תא)
                distance_cells = max(abs(row - start_row), abs(col - start_col))
                duration = distance_cells * 1000
                end_time = self._current_time_ms + duration
                
                # רישום כמהלך בתנועה
                self._pending_move = (start_row, start_col, row, col, piece_token, end_time)
                self._selected_cell = None
            else:
                self._selected_cell = None

    def handle_wait(self, ms: int) -> None:
        """מקדמת את זמן המשחק ובודקת סיום מהלכים."""
        self._current_time_ms += ms
        self._flush_pending_move_if_time_passed()

    def handle_print(self) -> None:
        """מדפיסה את הלוח המעודכן ביותר נכון למילישנייה הנוכחית."""
        self._flush_pending_move_if_time_passed()
        print(self._board.get_formatted_board())