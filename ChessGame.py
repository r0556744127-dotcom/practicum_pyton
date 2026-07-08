from ChessBoard import ChessBoard
from Piece import Piece

class ChessGame:
    """מנהלת את מצב המשחק, תורות השחקנים, והלוגיקה הדינמית של המהלכים."""
    
    def __init__(self, board: ChessBoard):
        self._board = board
        self._selected_cell = None  # שומר קואורדינטות (row, col) של הכלי הנבחר

    def handle_click(self, x: int, y: int) -> None:
        coords = self._board.convert_coordinates(x, y)
        if coords is None:
            return  # לחיצה מחוץ לגבולות הלוח - מתעלמים

        row, col = coords

        if self._selected_cell is None:
            # שלב הבחירה: בוחרים כלי רק אם המשבצת אינה ריקה
            if not self._board.is_empty_cell(row, col):
                self._selected_cell = (row, col)
        else:
            # שלב ביצוע המהלך
            start_row, start_col = self._selected_cell
            
            # אם לחצו על כלי ידידותי אחר - מחליפים את הבחירה לכלי החדש
            if self._board.is_friendly_piece(row, col, self._selected_cell):
                self._selected_cell = (row, col)
                return

            # שליפת סוג הכלי (לדוגמה 'wK' -> לוקחים את 'K')
            piece_token = self._board.get_piece_at(start_row, start_col)
            piece_type = piece_token[1]

            # בדיקת חוקיות התנועה באמצעות הפונקציה הגיאומטרית
            if Piece.is_legal_move(piece_type, start_row, start_col, row, col):
                # ביצוע המהלך ועדכון הלוח
                self._board.set_piece_at(row, col, piece_token)
                self._board.set_piece_at(start_row, start_col, '.')
                self._selected_cell = None  # איפוס הבחירה לאחר מהלך מוצלח
            else:
                # מהלך לא חוקי - מתעלמים ומבטלים את הבחירה הנוכחית
                self._selected_cell = None

    def handle_wait(self, ms: int) -> None:
        """מטפל בפקודת המתנה."""
        pass

    def handle_print(self) -> None:
        """מדפיס את מצב הלוח הנוכחי לקונסול."""
        print(self._board.get_formatted_board())