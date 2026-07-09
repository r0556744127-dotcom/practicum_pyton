import sys
import os

# מוצא את נתיב התיקייה שבה נמצא קובץ הטסט, ועולה רמה אחת למעלה (אל practicum_pyton)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# רק עכשיו, אחרי שהנתיב מעוגן ב-sys.path, ניקח את המודולים
import pytest
# שימי לב לאותיות הגדולות - בדיוק כמו שם הקובץ שלך!
from RuleEngine import RuleEngine 



# מחלקת דמה (Stub) המדמה את התנהגות הלוח לצורך הבדיקות
class FakeBoard:
    def __init__(self, rows=8, cols=8, grid=None):
        self.rows = rows
        self.cols = cols
        # ברירת מחדל: לוח ריק שמיוצג ע"י נקודות
        self.grid = grid or [['.' for _ in range(cols)] for _ in range(rows)]

    def get_dimensions(self):
        return self.rows, self.cols

    def get_piece_at(self, row, col):
        return self.grid[row][col]


# --- בדיקות עבור convert_pixel_to_cell ---

def test_convert_pixel_to_cell_valid():
    """בדיקה שהמרת פיקסלים בתוך הלוח מחזירה את התא הנכון"""
    board = FakeBoard(rows=8, cols=8)
    engine = RuleEngine(board)
    
    # פיקסל (150, 250) -> עמודה 1 (150 // 100), שורה 2 (250 // 100)
    assert engine.convert_pixel_to_cell(150, 250) == (2, 1)
    # בדיקת פיקסל בראשית הצירים (0,0)
    assert engine.convert_pixel_to_cell(0, 0) == (0, 0)

def test_convert_pixel_to_cell_out_of_bounds():
    """בדיקה שמיקום מחוץ לגבולות הלוח מחזיר None"""
    board = FakeBoard(rows=3, cols=3) # לוח קטן של 300x300 פיקסלים
    engine = RuleEngine(board)
    
    # פיקסל 350 חורג מלוח של 3 תאים (מקסימום 299)
    assert engine.convert_pixel_to_cell(350, 100) is None
    assert engine.convert_pixel_to_cell(100, -5) is None


# --- בדיקות עבור is_friendly ---

def test_is_friendly_same_color():
    """בדיקה ששני כלים מאותו צבע מחזירים True"""
    grid = [
        ['w_pawn', 'w_knight', '.'],
        ['.',      '.',        '.']
    ]
    board = FakeBoard(rows=2, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_friendly((0, 0), (0, 1)) is True

def test_is_friendly_different_colors():
    """בדיקה ששני כלים מצבעים שונים מחזירים False"""
    grid = [
        ['w_pawn', 'b_pawn', '.'],
        ['.',      '.',      '.']
    ]
    board = FakeBoard(rows=2, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_friendly((0, 0), (0, 1)) is False

def test_is_friendly_with_empty_cell():
    """בדיקה שאם אחד התאים (או שניהם) ריק, מחזיר False"""
    grid = [
        ['w_pawn', '.', '.'],
        ['.',      '.', '.']
    ]
    board = FakeBoard(rows=2, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_friendly((0, 0), (0, 1)) is False  # אחד ריק
    assert engine.is_friendly((0, 1), (0, 2)) is False  # שניהם ריקים

def test_is_friendly_invalid_input():
    """בדיקה שהעברת תא ריק (None) לא קורסת ומחזירה False"""
    board = FakeBoard()
    engine = RuleEngine(board)
    
    assert engine.is_friendly(None, (0, 0)) is False
    assert engine.is_friendly((0, 0), None) is False