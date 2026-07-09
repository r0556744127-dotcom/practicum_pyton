# import sys
# from Piece import Piece

# class ChessBoard:
#     """מנהלת את מבנה הנתונים הסטטי של הלוח ואכיפת חוקי המבנה."""
#     def __init__(self):
#         self._matrix = []
#         self._expected_width = None

#     def add_row(self, tokens) -> None:
#         """מוסיפה שורה ללוח ומבצעת בדיקות תקינות מיידיות."""
#         for token in tokens:
#             if not Piece.is_valid(token):
#                 print("ERROR UNKNOWN_TOKEN")
#                 sys.exit(0)

#         current_width = len(tokens)
#         if self._expected_width is None:
#             self._expected_width = current_width
#         elif current_width != self._expected_width:
#             print("ERROR ROW_WIDTH_MISMATCH")
#             sys.exit(0)

#         self._matrix.append(tokens)

#     def is_empty(self) -> bool:
#         return len(self._matrix) == 0

#     def get_formatted_board(self) -> str:
#         return "\n".join(" ".join(row) for row in self._matrix)
    
#     def convert_coordinates(self, x: int, y: int):
#         """ממירה קואורדינטות פיקסלים לתא בלוח (row, col)."""
#         col = x // 100
#         row = y // 100

#         if 0 <= row < len(self._matrix) and 0 <= col < self._expected_width:
#             return row, col
#         return None

#     def get_piece_at(self, row: int, col: int) -> str:
#         return self._matrix[row][col]

#     def set_piece_at(self, row: int, col: int, piece_token: str) -> None:
#         self._matrix[row][col] = piece_token

#     def is_empty_cell(self, row: int, col: int) -> bool:
#         return self.get_piece_at(row, col) == '.'

#     def is_friendly_piece(self, row: int, col: int, current_selection) -> bool:
#         if current_selection is None:
#             return False
#         sel_row, sel_col = current_selection
#         p1 = self.get_piece_at(row, col)
#         p2 = self.get_piece_at(sel_row, sel_col)
#         if p1 == '.' or p2 == '.':
#             return False
#         return p1[0] == p2[0]