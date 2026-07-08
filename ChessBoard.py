class ChessBoard:
    """מייצגת את לוח המשחק, מנהלת את משבצות הלוח ובודקת תקינות מיקומים."""
    
    def __init__(self, cell_size: int = 100):
        self._grid = []
        self.cell_size = cell_size

    def add_row(self, row_tokens: list) -> None:
        """מוסיפה שורה חדשה של תאים ללוח."""
        self._grid.append(row_tokens)

    def get_piece_at(self, row: int, col: int) -> str:
        """מחזירה את ייצוג הכלי במיקום המבוקש."""
        if 0 <= row < len(self._grid) and 0 <= col < len(self._grid[row]):
            return self._grid[row][col]
        return '.'

    def set_piece_at(self, row: int, col: int, piece: str) -> None:
        """מציבה כלי במיקום המבוקש בלוח."""
        if 0 <= row < len(self._grid) and 0 <= col < len(self._grid[row]):
            self._grid[row][col] = piece

    def is_empty_cell(self, row: int, col: int) -> bool:
        """בודקת האם המשבצת נתונה ריקה."""
        return self.get_piece_at(row, col) == '.'

    def is_friendly_piece(self, row: int, col: int, selected_cell: tuple) -> bool:
        """בודקת האם המשבצת ביעד מכילה כלי מאותו הצבע של הכלי שנבחר."""
        target_piece = self.get_piece_at(row, col)
        if target_piece == '.':
            return False
            
        start_row, start_col = selected_cell
        selected_piece = self.get_piece_at(start_row, start_col)
        
        # השוואת התו הראשון (w או b)
        return target_piece[0] == selected_piece[0]

    def convert_coordinates(self, x: int, y: int) -> tuple:
        """ממירה קואורדינטות פיזיות (פיקסלים) לאינדקסים במטריצה (שורה, עמודה)."""
        col = x // self.cell_size
        row = y // self.cell_size
        
        if 0 <= row < len(self._grid) and len(self._grid) > 0 and 0 <= col < len(self._grid[0]):
            return (row, col)
        return None

    def get_formatted_board(self) -> str:
        """מחזירה את תצוגת הלוח כמחרוזת מוכנה להדפסה."""
        return '\n'.join(' '.join(row) for row in self._grid)