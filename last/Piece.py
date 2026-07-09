# class Piece:
#     """אחראית על הגדרת ותקינות כלי שחמט בודד."""
#     VALID_TOKENS = {
#         '.', 
#         'wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
#         'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'
#     }

#     @staticmethod
#     def is_valid(token: str) -> bool:
#         return token in Piece.VALID_TOKENS