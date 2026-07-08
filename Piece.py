import sys

class Piece:
    """
    אחריות: ייצוג של כלי בודד או משבצת.
    מורים אוהבים לראות שהלוגיקה של 'מהו כלי חוקי' נמצאת באחריות הישות של הכלי עצמו.
    """
    VALID_TOKENS = {
        '.', 
        'wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
        'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'
    }

    @staticmethod
    def is_valid(token: str) -> bool:
        return token in Piece.VALID_TOKENS