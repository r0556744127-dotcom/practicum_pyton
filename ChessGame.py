# "ניהול מצב הדינאמי של המשחק"

class ChessGame:
    def __init__(self, board):
        self.board = board
        self.selected_cell = None  # ישמור (row, col) אם נבחר כלי, אחרת None
        self.game_clock_ms = 0     # שעון המשחק במילישניות

    def handle_click(self, x: int, y: int) -> None:
        """מנהלת את לוגיקת הלחיצות על פי חוקי המשחק."""
        # 1. המרת קואורדינטות ובדיקת גבולות (באמצעות הלוח)
        coords = self.board.convert_coordinates(x, y)
        if coords is None:
            return  # לחיצה מחוץ ללוח - מתעלמים לחלוטין

        row, col = coords

        # 2. לוגיקת בחירה והזזה
        # מצב א': אין כלי נבחר כרגע
        if self.selected_cell is None:
            if self.board.is_empty_cell(row, col):
                return  # לחיצה על תא ריק ללא בחירה - מתעלמים
            else:
                self.selected_cell = (row, col)  # לחיצה על כלי בוחרת אותו
                
        # מצב ב': כבר יש כלי נבחר מקודם
        else:
            # אם לחצנו על כלי ידידותי אחר -> מחליפים את הבחירה
            if self.board.is_friendly_piece(row, col, self.selected_cell):
                self.selected_cell = (row, col)
            else:
                # לחצנו על תא אחר (ריק או אויב) -> שולחים בקשת העברה
                src_row, src_col = self.selected_cell
                self._execute_move(src_row, src_col, row, col)
                self.selected_cell = None  # מאפסים את הבחירה לאחר המהלך

  
    def handle_wait(self, ms: int) -> None:
        """מקדם את שעון המשחק במספר המילישניות הנתון."""
        self.game_clock_ms += ms

    def handle_print(self) -> None:
        if not self.board.is_empty():
            print(self.board.get_formatted_board())