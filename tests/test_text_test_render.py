import pytest
from unittest.mock import MagicMock
# ייבוא המחלקות משורש הפרויקט
from Render import TextTestRender

def test_display_valid_matrix(capsys):
    """בדיקה שהמחלקה מדפיסה את הלוח בצורה קנונית עם רווחים בין הכלים וירידת שורה"""
    render_engine = TextTestRender()
    
    # יצירת מוק עבור ה-Snapshot והגדרת המטריצה שלו
    mock_snapshot = MagicMock()
    fake_matrix = [
        ['wR', 'wN', 'wB'],
        ['.', 'wK', '.'],
        ['bR', 'bN', 'bB']
    ]
    
    # תמיכה בשמות השדות השונים (matrix או board_matrix)
    mock_snapshot.matrix = fake_matrix
    mock_snapshot.board_matrix = fake_matrix

    # הפעלת פונקציית התצוגה
    render_engine.display(mock_snapshot)

    # תפיסת הפלט שהודפס למסך
    captured = capsys.readouterr()
    
    # הפלט הצפוי - הכלים מופרדים ברווחים, וכל שורה מופרדת בירידת שורה
    expected_output = "wR wN wB\n. wK .\nbR bN bB\n"
    
    assert captured.out == expected_output


def test_display_empty_or_missing_matrix(capsys):
    """בדיקה שבמידה והמטריצה ריקה או לא קיימת, לא מודפס דבר ומערכת לא קורסת"""
    render_engine = TextTestRender()
    
    mock_snapshot = MagicMock()
    mock_snapshot.matrix = None
    mock_snapshot.board_matrix = None

    render_engine.display(mock_snapshot)

    captured = capsys.readouterr()
    assert captured.out == ""