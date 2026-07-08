class ChessGame:
    def __init__(self, board):
        self.board = board
        self.selected_cell = None  # ישמור (row, col) אם נבחר כלי
        self.game_clock_ms = 0     # שעון המשחק

    def handle_click(self, x: int, y: int) -> None:
        """מנהלת את לוגיקת הלחיצות על פי חוקי המשחק."""
        coords = self.board.convert_coordinates(x, y)
        if coords is None:
            return  # מחוץ ללוח - מתעלמים

        row, col = coords

        # מצב א': אין כלי נבחר כרגע
        if self.selected_cell is None:
            if self.board.is_empty_cell(row, col):
                return  # תא ריק ללא בחירה - מתעלמים
            else:
                self.selected_cell = (row, col)  # בחירת כלי
                
        # מצב ב': יש כבר כלי נבחר
        else:
            if self.board.is_friendly_piece(row, col, self.selected_cell):
                self.selected_cell = (row, col)  # החלפת בחירה בכלי ידידותי
            else:
                # לחיצה על תא אחר -> ביצוע המהלך
                src_row, src_col = self.selected_cell
                self._execute_move(src_row, src_col, row, col)
                self.selected_cell = None  # איפוס הבחירה

    def _execute_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> None:
        """מבצעת העברת כלי ממשבצת אחת למשבצת שנייה ומעדכנת את הלוח."""
        piece = self.board.get_piece_at(from_row, from_col)
        self.board.set_piece_at(from_row, from_col, '.')
        self.board.set_piece_at(to_row, to_col, piece)

    def handle_wait(self, ms: int) -> None:
        self.game_clock_ms += ms

    def handle_print(self) -> None:
        if not self.board.is_empty():
            print(self.board.get_formatted_board())