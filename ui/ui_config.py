import os

# ============================================
#  ui_config.py — הגדרות UI בלבד
# ============================================

# --- נתיבים ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIECES_ROOT = os.path.join(BASE_DIR, "pieces")
BOARD_IMAGE = os.path.join(BASE_DIR, "board.png")

# --- גודל משבצת (לציור) ---
# חייב להיות זהה ל-GameController.CELL_SIZE (= 100)
CELL_SIZE_PX = 100

# --- תרגום מטרים ↔ פיקסלים ---
METERS_PER_CELL = 1.0
PX_PER_METER = CELL_SIZE_PX / METERS_PER_CELL

# --- אנימציה ---
ALL_STATES = ("idle", "move", "jump", "long_rest", "short_rest")
STATE_TRANSITIONS = {
    "move":       "long_rest",
    "jump":       "short_rest",
    "long_rest":  "idle",
    "short_rest": "idle",
    "idle":       "idle",
}

# --- חלון ---
WINDOW_NAME = "Kung-Fu Chess"
WINDOW_WIDTH  = CELL_SIZE_PX * 8
WINDOW_HEIGHT = CELL_SIZE_PX * 8

# --- צבעים (BGRA) ---
COLOR_SCORE  = (0, 255, 0, 255)
COLOR_TEXT   = (255, 255, 255, 255)
COLOR_MARKER = (0, 0, 255, 255)

# --- ניקוד (שלב 8) ---
CAPTURE_POINTS = {
    "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0,
}