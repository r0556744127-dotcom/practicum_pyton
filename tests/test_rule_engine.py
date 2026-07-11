import sys
import os
from unittest.mock import MagicMock
import pytest

# מוצא את נתיב התיקייה שבה נמצא קובץ הטסט, ועולה רמה אחת למעלה
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from MappBoard import MappBoard
from RuleEngine import RuleEngine 


# --- מחלקת דמה (Stub) המדמה את התנהגות הלוח לצורך הבדיקות ---
class FakeBoard:
    def __init__(self, rows=8, cols=8, grid=None):
        self.rows = rows
        self.cols = cols
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
    
    assert engine.convert_pixel_to_cell(150, 250) == (2, 1)
    assert engine.convert_pixel_to_cell(0, 0) == (0, 0)


def test_convert_pixel_to_cell_out_of_bounds():
    """בדיקה שמיקום מחוץ לגבולות הלוח מחזיר None"""
    board = FakeBoard(rows=3, cols=3)
    engine = RuleEngine(board)
    
    assert engine.convert_pixel_to_cell(350, 100) is None
    assert engine.convert_pixel_to_cell(100, -5) is None


# --- בדיקות עבור is_friendly ---

def test_is_friendly_same_color():
    """בדיקה ששני כלים מאותו צבע מחזירים True"""
    grid = [
        ['w_pawn', 'w_knight', '.'],
        ['.',       '.',        '.']
    ]
    board = FakeBoard(rows=2, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_friendly((0, 0), (0, 1)) is True


def test_is_friendly_different_colors():
    """בדיקה ששני כלים מצבעים שונים מחזירים False"""
    grid = [
        ['w_pawn', 'b_pawn', '.'],
        ['.',       '.',      '.']
    ]
    board = FakeBoard(rows=2, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_friendly((0, 0), (0, 1)) is False


def test_is_friendly_with_empty_cell():
    """בדיקה שאם אחד התאים (או שניהם) ריק, מחזיר False"""
    grid = [
        ['w_pawn', '.', '.'],
        ['.',       '.', '.']
    ]
    board = FakeBoard(rows=2, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_friendly((0, 0), (0, 1)) is False
    assert engine.is_friendly((0, 1), (0, 2)) is False


def test_is_friendly_invalid_input():
    """בדיקה שהעברת תא ריק (None) לא קורסת ומחזירה False"""
    board = FakeBoard()
    engine = RuleEngine(board)
    
    assert engine.is_friendly(None, (0, 0)) is False
    assert engine.is_friendly((0, 0), None) is False


# --- בדיקות חוסמים, דילוגים ומסלול ---

def test_rule_engine_path_clear_rook_blocked():
    """בדיקה שצריח (R) מזוהה כחסום כאשר יש כלי במסלול הישר שלו"""
    grid = [
        ['wR', 'wP', '.'],
        ['.',  '.',  '.']
    ]
    board = FakeBoard(rows=2, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_path_clear((0, 0), (0, 2)) is False


def test_rule_engine_path_clear_bishop_clear():
    """בדיקה שרץ (B) מזהה מסלול פנוי באלכסון כשאין חוסמים"""
    grid = [
        ['wB', '.',  '.'],
        ['.',  '.',  '.'],
        ['.',  '.',  '.']
    ]
    board = FakeBoard(rows=3, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_path_clear((0, 0), (2, 2)) is True


def test_rule_engine_knight_can_jump():
    """בדיקה שפרש (N) תמיד רשאי לדלג מעל כלים חוסמים"""
    grid = [
        ['wN', 'bP', '.'],
        ['.',  '.',  '.'],
        ['.',  '.',  '.']
    ]
    board = FakeBoard(rows=3, cols=3, grid=grid)
    engine = RuleEngine(board)
    
    assert engine.is_path_clear((0, 0), (2, 1)) is True


def test_click_outside_board():
    board = MappBoard()
    board.add_row(["wK"])
    engine = RuleEngine(board)
    assert engine.convert_pixel_to_cell(200, 200) is None


def test_friendly_pieces():
    board = MappBoard()
    board.add_row(["wK", "wR"])
    engine = RuleEngine(board)
    assert engine.is_friendly((0, 0), (0, 1)) 


def test_enemy_pieces():
    board = MappBoard()
    board.add_row(["wK", "bK"])
    engine = RuleEngine(board)
    assert not engine.is_friendly((0, 0), (0, 1))      


def test_pixel_to_cell():
    board = MappBoard()
    board.add_row(["wK", "."])
    board.add_row([".", "."])
    engine = RuleEngine(board)
    assert engine.convert_pixel_to_cell(50, 50) == (0, 0)
    assert engine.convert_pixel_to_cell(150, 50) == (0, 1)


def test_game_engine_capture_enemy():
    """בדיקה שלחיצה על כלי אויב במסלול פנוי מבצעת הכאה בהצלחה"""
    from GameEngine import GameEngine
    
    board = MappBoard()
    board.add_row(['wR', '.', 'bP'])
    
    # הוספת delayed_movement=False כדי שהתנועה תבוצע מייד בטסט
    engine = GameEngine(board, delayed_movement=False)

    engine.handle_click(50, 50)    # לחיצה ראשונה: בחירת הצריח (0,0)
    engine.handle_click(250, 50)   # לחיצה שנייה: תנועה ליעד והכאת האויב (0,2)
    
    # כעת התנועה בוצעה מיידית והמשבצת המקורית אכן ריקה
    assert board.get_piece_at(0, 0) == '.'
    assert board.get_piece_at(0, 2) == 'wR'
# --- בדיקות מבוססות Mock (הוסרו מתודות ה-self לטובת סגנון pytest נקי) ---

def test_is_path_clear_same_source_and_destination_returns_false():
    """מוודא שלחיצה על אותו תא בדיוק נעצרת מיד ומחזירה False למניעת לולאה אינסופית."""
    mock_board = MagicMock()
    engine = RuleEngine(mock_board)
    
    src = (3, 3)
    dst = (3, 3)
    
    assert engine.is_path_clear(src, dst) is False


def test_is_path_clear_when_source_is_empty():
    """מוודא שאם תא המקור ריק באופן בלתי צפוי, הפונקציה מחזירה False."""
    mock_board = MagicMock()
    mock_board.get_piece_at.return_value = '.'
    engine = RuleEngine(mock_board)
    
    src = (1, 1)
    dst = (1, 4)
    
    assert engine.is_path_clear(src, dst) is False


def test_is_path_clear_with_blocker_returns_false():
    """בודק שכלי ליניארי מזהה חוסם באמצע הדרך ומחזיר False."""
    mock_board = MagicMock()
    
    def side_effect_board(row, col):
        if (row, col) == (0, 0): return 'wR'
        if (row, col) == (0, 2): return 'bP'  # חוסם באמצע המסלול
        return '.'
        
    mock_board.get_piece_at.side_effect = side_effect_board
    engine = RuleEngine(mock_board)
    
    src = (0, 0)
    dst = (0, 4)
    
    assert engine.is_path_clear(src, dst) is False


def test_is_path_clear_with_enemy_at_destination_only_returns_true():
    """מוודא שכלי אויב שנמצא *רק במשבצת היעד* אינו חוסם את המסלול (מאפשר הכאה)."""
    mock_board = MagicMock()
    
    def side_effect_board(row, col):
        if (row, col) == (0, 0): return 'wR'
        if (row, col) == (0, 3): return 'bP'  # כלי אויב שנמצא על היעד
        return '.'
        
    mock_board.get_piece_at.side_effect = side_effect_board
    engine = RuleEngine(mock_board)
    
    src = (0, 0)
    dst = (0, 3)
    
    assert engine.is_path_clear(src, dst) is True