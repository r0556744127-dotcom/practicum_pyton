
import pytest
from unittest.mock import MagicMock
# ייבוא מהקובץ MappBoard.py שנמצא בשורש הפרויקט
from MappBoard import MappBoard
# מייבאים את PieceRules כדי שנוכל לעשות לו מוק
import PieceRules

@pytest.fixture(autouse=True)
def mock_piece_rules(monkeypatch):
    """מחליף זמנית את הפונקציה האמיתית במוק, רק עבור קובץ הטסטים הזה"""
    mock_func = MagicMock(return_value=True)
    monkeypatch.setattr(PieceRules.PieceRules, "is_valid_token", mock_func)
    return mock_func

def test_add_row_success():
    """בדיקה שהוספת שורות תקינות בונה את המטריצה כראוי ומעדכנת מימדים"""
    board = MappBoard()
    
    board.add_row(['wK', '.', 'bK'])
    board.add_row(['.', 'wP', '.'])
    
    assert board.get_dimensions() == (2, 3)
    assert board.get_piece_at(0, 0) == 'wK'
    assert board.get_piece_at(1, 1) == 'wP'


def test_get_raw_matrix_returns_deep_copy():
    """בדיקה שחילוץ המטריצה מחזיר העתק עמוק ולא משפיע על הלוח המקורי"""
    board = MappBoard()
    board.add_row(['wK', '.'])
    
    raw_matrix = board.get_raw_matrix()
    # שינוי בהעתק שקיבלנו
    raw_matrix[0][0] = 'bQ'
    
    # הלוח המקורי חייב להישאר ללא שינוי
    assert board.get_piece_at(0, 0) == 'wK'


def test_set_piece_at():
    """בדיקה שעדכון כלי בתא ספציפי עובד בהצלחה"""
    board = MappBoard()
    board.add_row(['.', '.'])
    
    board.set_piece_at(0, 1, 'wR')
    
    assert board.get_piece_at(0, 1) == 'wR'


def test_add_row_unknown_token_error(capsys, mock_piece_rules):
    """בדיקה שתג לא מוכר מדפיס שגיאה מתאימה ומסיים את התוכנית"""
    # משנים את המוק המקומי שקיבלנו מהפיקסטורה ל-False
    mock_piece_rules.return_value = False
    
    board = MappBoard()
    
    with pytest.raises(SystemExit):
        board.add_row(['INVALID_TOKEN'])
        
    captured = capsys.readouterr()
    assert "ERROR UNKNOWN_TOKEN" in captured.out
def test_add_row_width_mismatch_error(capsys):
    """בדיקה שהוספת שורה באורך שונה מהשורה הראשונה קורסת עם שגיאה מתאימה"""
    board = MappBoard()
    
    # שורה ראשונה באורך 3
    board.add_row(['.', '.', '.'])
    
    # שורה שנייה באורך 2 (חוסר התאמה)
    with pytest.raises(SystemExit):
        board.add_row(['.', '.'])
        
    captured = capsys.readouterr()
    assert "ERROR ROW_WIDTH_MISMATCH" in captured.out