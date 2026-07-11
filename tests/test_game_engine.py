import pytest
from MappBoard import MappBoard
from GameEngine import GameEngine
from unittest.mock import MagicMock
from GameSnapshot import GameSnapshot

@pytest.fixture
def mock_dependencies():
    """פיקסטורה המייצרת מוקים נקיים ללוח ולמנוע החוקים עבור כל טסט"""
    board = MagicMock()
    rule_engine = MagicMock()
    return board, rule_engine

@pytest.fixture
def engine(mock_dependencies):
    """פיקסטורה שמאתחלת את מנוע המשחק עם המוקים שהגדרנו"""
    board, rule_engine = mock_dependencies
    
    game_eng = GameEngine(board)
    game_eng.rule_engine = rule_engine
    
    return game_eng, board, rule_engine


# --- בדיקות עבור handle_click ---

def test_handle_click_out_of_bounds(engine):
    game_eng, board, rule_engine = engine
    rule_engine.convert_pixel_to_cell.return_value = None
    game_eng.handle_click(500, 500)
    assert game_eng.selected_cell is None
    board.get_piece_at.assert_not_called()


def test_handle_click_select_piece(engine):
    game_eng, board, rule_engine = engine
    rule_engine.convert_pixel_to_cell.return_value = (2, 3)
    board.get_piece_at.return_value = 'wP'
    game_eng.handle_click(250, 350)
    assert game_eng.selected_cell == (2, 3)
    board.get_piece_at.assert_called_once_with(2, 3)


def test_handle_click_select_empty_cell(engine):
    game_eng, board, rule_engine = engine
    rule_engine.convert_pixel_to_cell.return_value = (0, 0)
    board.get_piece_at.return_value = '.'
    game_eng.handle_click(50, 50)
    assert game_eng.selected_cell is None


def test_handle_click_switch_selection(engine):
    game_eng, board, rule_engine = engine
    game_eng.selected_cell = (0, 0)
    rule_engine.convert_pixel_to_cell.return_value = (0, 1)
    board.get_piece_at.return_value = 'wK'
    rule_engine.is_friendly.return_value = True
    game_eng.handle_click(50, 150)
    assert game_eng.selected_cell == (0, 1)


def test_handle_click_execute_move(engine):
    game_eng, board, rule_engine = engine
    game_eng.selected_cell = (1, 1)
    board.get_piece_at.side_effect = lambda r, c: 'wP' if (r, c) == (1, 1) else '.'
    rule_engine.convert_pixel_to_cell.return_value = (2, 2)
    rule_engine.is_friendly.return_value = False
    game_eng.handle_click(250, 250)
    assert game_eng.selected_cell is None
    board.set_piece_at.assert_any_call(1, 1, '.')
    board.set_piece_at.assert_any_call(2, 2, 'wP')


# --- בדיקות עבור handle_wait ו-create_snapshot ---

def test_handle_wait_updates_clock(engine):
    game_eng, _, _ = engine
    game_eng.handle_wait(150)
    assert game_eng.game_clock_ms == 150


def test_create_snapshot(engine):
    game_eng, board, _ = engine
    game_eng.game_clock_ms = 450
    fake_matrix = [['.', 'wK'], ['bK', '.']]
    board.get_raw_matrix.return_value = fake_matrix
    snapshot = game_eng.create_snapshot()
    assert isinstance(snapshot, GameSnapshot)


# --- בדיקות אינטגרציה ---

def test_move_piece():
    board = MappBoard()
    board.add_row(["wK", "."])
    board.add_row([".", "."])
    game = GameEngine(board, delayed_movement=False) # כיבוי השהיה לטסט רגיל
    game.handle_click(50, 50)
    game.handle_click(150, 150)
    assert board.get_piece_at(1, 1) == "wK"


# --- בדיקות חדשות (זמן) ---

def test_move_over_time_before_duration_keeps_original_position():
    board = MappBoard()
    board.add_row(["wK", "."])
    board.add_row([".", "."])
    game = GameEngine(board, delayed_movement=True)
    game.handle_click(50, 50)
    game.handle_click(150, 150)
    assert board.get_piece_at(0, 0) == "wK"


def test_move_over_time_after_sufficient_wait_reaches_destination():
    board = MappBoard()
    board.add_row(["wK", "."])
    board.add_row([".", "."])
    game = GameEngine(board, delayed_movement=True)
    game.handle_click(50, 50)
    game.handle_click(150, 150)
    game.handle_wait(2000) # תואם לנוסחת ה-distance * 1000
    assert board.get_piece_at(1, 1) == "wK"
def test_prevent_movement_while_in_progress():
    """בדיקה שלא ניתן להזיז כלי אחר או את אותו כלי בזמן שיש תנועה בתהליך"""
    board = MappBoard()
    board.add_row(["wK", ".", "."])
    board.add_row([".", ".", "."])
    
    # שימוש ב-delayed_movement=True כדי שהתנועה תיקח זמן
    game = GameEngine(board, delayed_movement=True)
    
    # בחירה והתחלת תנועה
    game.handle_click(50, 50)   # בוחר wK ב-(0,0)
    game.handle_click(250, 50)  # מתחיל תנועה ל-(0,2)
    
    # עכשיו המנוע ב-pending_move. ננסה ללחוץ שוב
    game.handle_click(50, 50)   # לחיצה נוספת
    
    # הבדיקה: הלוח לא אמור להשתנות כי התנועה הראשונה עדיין בעיצומה
    assert board.get_piece_at(0, 0) == "wK" 
    assert board.get_piece_at(0, 2) == "."


def test_immediate_movement_after_completion():
    """בדיקה שאחרי סיום תנועה, ניתן להזיז כלי מיד ללא צורך בהמתנה נוספת"""
    board = MappBoard()
    board.add_row(["wK", ".", "."])
    board.add_row([".", ".", "."])
    
    game = GameEngine(board, delayed_movement=True)
    
    # מהלך ראשון
    game.handle_click(50, 50)   # (0,0)
    game.handle_click(150, 50)  # (0,1)
    
    # סיום המהלך הראשון
    game.handle_wait(1000) 
    assert board.get_piece_at(0, 1) == "wK"
    
    # מהלך שני מיידי (בדיקה שאין 'קירור')
    game.handle_click(150, 50)  # בחירה מ-(0,1)
    game.handle_click(250, 50)  # תנועה ל-(0,2)
    
    # סיום המהלך השני
    game.handle_wait(1000)
    assert board.get_piece_at(0, 2) == "wK"
    assert board.get_piece_at(0, 1) == "."    