"""הרצת שלב 1 — ציור לוח סטטי. להריץ מתוך תיקיית הפרויקט:
   python draw_demo.py
"""
from board_parser import BoardParser
from ui_helpers import draw_static_board

# לוח התחלתי מלא (8x8) — בלי צורך להקליד ב-stdin
STARTING_BOARD = [
    "Board:",
    "bR bN bB bQ bK bB bN bR",
    "bP bP bP bP bP bP bP bP",
    ". . . . . . . .",
    ". . . . . . . .",
    ". . . . . . . .",
    ". . . . . . . .",
    "wP wP wP wP wP wP wP wP",
    "wR wN wB wQ wK wB wN wR",
]

if __name__ == "__main__":
    parser = BoardParser()
    board, _ = parser.parse(STARTING_BOARD)
    draw_static_board(board)
