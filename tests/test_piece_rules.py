import pytest
# ייבוא מהקובץ PieceRules.py שנמצא בשורש הפרויקט
from PieceRules import PieceRules

def test_is_valid_token_valid_pieces():
    """בדיקה שכל הכלים החוקיים (לבנים ושחורים) ותא ריק מחזירים True"""
    # תא ריק חוקי
    assert PieceRules.is_valid_token('.') is True
    
    # כלים לבנים חוקיים
    assert PieceRules.is_valid_token('wK') is True
    assert PieceRules.is_valid_token('wQ') is True
    assert PieceRules.is_valid_token('wP') is True
    
    # כלים שחורים חוקיים
    assert PieceRules.is_valid_token('bK') is True
    assert PieceRules.is_valid_token('bR') is True
    assert PieceRules.is_valid_token('bN') is True

def test_is_valid_token_invalid_pieces():
    """בדיקה שתגים שאינם קיימים בחוקים מחזירים False"""
    assert PieceRules.is_valid_token('wX') is False  # אות כלי לא קיימת
    assert PieceRules.is_valid_token('zK') is False  # צבע לא קיים
    assert PieceRules.is_valid_token('WK') is False  # אות גדולה במקום קטנה לצבע
    assert PieceRules.is_valid_token('wp') is False  # אות קטנה במקום גדולה לכלי

def test_is_valid_token_edge_cases():
    """בדיקה של מקרי קצה כמו מחרוזת ריקה, ארוכה מדי או ערך None"""
    assert PieceRules.is_valid_token('') is False       # מחרוזת ריקה
    assert PieceRules.is_valid_token('wKK') is False    # ארוך מדי
    assert PieceRules.is_valid_token('w') is False      # קצר מדי
    assert PieceRules.is_valid_token(None) is False     # ערך ריק