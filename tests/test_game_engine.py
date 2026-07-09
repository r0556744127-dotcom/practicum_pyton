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
    """בדיקה שלחיצה מחוץ ללוח (convert_pixel_to_cell מחזיר None) לא משנה דבר"""
    game_eng, board, rule_engine = engine
    rule_engine.convert_pixel_to_cell.return_value = None

    game_eng.handle_click(500, 500)

    assert game_eng.selected_cell is None
    board.get_piece_at.assert_not_called()


def test_handle_click_select_piece(engine):
    """בדיקה שלחיצה ראשונה על תא עם כלי בוחרת את התא בהצלחה"""
    game_eng, board, rule_engine = engine
    rule_engine.convert_pixel_to_cell.return_value = (2, 3)
    board.get_piece_at.return_value = 'wP'

    game_eng.handle_click(250, 350)

    assert game_eng.selected_cell == (2, 3)
    board.get_piece_at.assert_called_once_with(2, 3)


def test_handle_click_select_empty_cell(engine):
    """בדיקה שלחיצה ראשונה על תא ריק לא בוחרת אותו"""
    game_eng, board, rule_engine = engine
    rule_engine.convert_pixel_to_cell.return_value = (0, 0)
    board.get_piece_at.return_value = '.'

    game_eng.handle_click(50, 50)

    assert game_eng.selected_cell is None


def test_handle_click_switch_selection(engine):
    """בדיקה שלחיצה על כלי חברותי כשיש כבר כלי נבחר מחליפה את הבחירה"""
    game_eng, board, rule_engine = engine
    
    game_eng.selected_cell = (0, 0)
    
    rule_engine.convert_pixel_to_cell.return_value = (0, 1)
    board.get_piece_at.return_value = 'wK'
    rule_engine.is_friendly.return_value = True

    game_eng.handle_click(50, 150)

    assert game_eng.selected_cell == (0, 1)
    rule_engine.is_friendly.assert_called_once_with((0, 1), (0, 0))


def test_handle_click_execute_move(engine):
    """בדיקה שלחיצה על תא יעד חוקי (לא חברותי) מבצעת תנועה ומאפסת את הבחירה"""
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
    """בדיקה שזמן ההמתנה מתווסף נכון לשעון המשחק"""
    game_eng, _, _ = engine
    assert game_eng.game_clock_ms == 0

    game_eng.handle_wait(150)
    assert game_eng.game_clock_ms == 150

    game_eng.handle_wait(50)
    assert game_eng.game_clock_ms == 200


def test_create_snapshot(engine):
    """בדיקה שייצור ה-Snapshot מחזיר אובייקט עם הנתונים העדכניים מהלוח ומהשעון"""
    game_eng, board, _ = engine
    game_eng.game_clock_ms = 450
    fake_matrix = [['.', 'wK'], ['bK', '.']]
    board.get_raw_matrix.return_value = fake_matrix

    snapshot = game_eng.create_snapshot()

    assert isinstance(snapshot, GameSnapshot)
    
    # בדיקה דינמית וגמישה לשעון: מחפש game_clock_ms, clock, או clock_ms
    actual_clock = getattr(snapshot, 'game_clock_ms', 
                   getattr(snapshot, 'clock', 
                   getattr(snapshot, 'clock_ms', None)))
    assert actual_clock == 450
    
    # בדיקה דינמית וגמישה למטריצה: מחפש board_matrix או matrix
    actual_matrix = getattr(snapshot, 'board_matrix', 
                    getattr(snapshot, 'matrix', None))
    assert actual_matrix == fake_matrix
# בחירת כלי
def test_select_piece():

    board=MappBoard()
    board.add_row(["wK","."])

    game=GameEngine(board)

    game.handle_click(50,50)

    assert game.selected_cell==(0,0)  
# לחיצה על ריק לא בוחרת    
def test_empty_click():

    board=MappBoard()
    board.add_row([".","wK"])

    game=GameEngine(board)

    game.handle_click(50,50)

    assert game.selected_cell is None
# הזזת מלך    
def test_move_piece():

    board=MappBoard()
    board.add_row(["wK","."])
    board.add_row([".","."])

    game=GameEngine(board)

    game.handle_click(50,50)
    game.handle_click(150,150)

    assert board.get_piece_at(1,1)=="wK"
    assert board.get_piece_at(0,0)=="."      
# תנועה לא חוקית    
def test_invalid_move_not_done():

    board=MappBoard()
    board.add_row(["wK",".","."])
    board.add_row([".",".","."])
    board.add_row([".",".","."])

    game=GameEngine(board)

    game.handle_click(50,50)
    game.handle_click(250,250)

    assert board.get_piece_at(0,0)=="wK"
# החלפת בחירה    
def test_switch_selection():

    board=MappBoard()
    board.add_row(["wR","wK"])

    game=GameEngine(board)

    game.handle_click(50,50)
    game.handle_click(150,50)

    assert game.selected_cell==(0,1)        