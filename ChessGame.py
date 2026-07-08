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
            return

        row, col = coords

        if self._selected_cell is None:
            if not self._board.is_empty_cell(row, col):
                self._selected_cell = (row, col)
        else:
            start_row, start_col = self._selected_cell
            
            # אם השחקן לוחץ על כלי אחר מאותו הצבע, נחליף את הבחירה לכלי החדש
            if self._board.is_friendly_piece(row, col, self._selected_cell):
                self._selected_cell = (row, col)
                return

            # בדיקת חוקיות המהלך המלאה (כולל חוסמים ואכילה)
            if Piece.is_legal_move(self._board, start_row, start_col, row, col):
                piece_token = self._board.get_piece_at(start_row, start_col)
                
                # ביצוע המהלך (אם היה שם כלי אויב, הוא פשוט נדרס/נאכל)
                self._board.set_piece_at(row, col, piece_token)
                self._board.set_piece_at(start_row, start_col, '.')
                self._selected_cell = None
            else:
                # מהלך לא חוקי - מבטלים את הבחירה
                self._selected_cell = None
    def handle_wait(self, ms: int) -> None:
        """מטפל בפקודת המתנה."""
        pass

    def handle_print(self) -> None:
        """מדפיס את מצב הלוח הנוכחי לקונסול."""
        print(self._board.get_formatted_board())