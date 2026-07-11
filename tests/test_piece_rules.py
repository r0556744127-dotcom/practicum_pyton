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
def test_king_one_step_valid():
    assert PieceRules.can_king_move(0,0,1,1) == True


def test_king_horizontal_one_step_valid():
    assert PieceRules.can_king_move(0,0,0,1) == True


def test_king_two_steps_invalid():
    assert PieceRules.can_king_move(0,0,2,2) == False


def test_king_same_place_invalid():
    assert PieceRules.can_king_move(1,1,1,1) == False
def test_rook_vertical_valid():
    assert PieceRules.can_rook_move(0,0,2,0) == True


def test_rook_horizontal_valid():
    assert PieceRules.can_rook_move(0,0,0,3) == True


def test_rook_diagonal_invalid():
    assert PieceRules.can_rook_move(0,0,2,2) == False
def test_bishop_diagonal_valid():
    assert PieceRules.can_bishop_move(0,0,3,3) == True


def test_bishop_straight_invalid():
    assert PieceRules.can_bishop_move(0,0,3,0) == False
def test_knight_L_valid():
    assert PieceRules.can_knight_move(0,0,2,1) == True


def test_knight_invalid():
    assert PieceRules.can_knight_move(0,0,2,2) == False
def test_queen_diagonal_valid():
    assert PieceRules.can_queen_move(0,0,3,3) == True


def test_queen_straight_valid():
    assert PieceRules.can_queen_move(0,0,0,4) == True


def test_queen_invalid():
    assert PieceRules.can_queen_move(0,0,1,2) == False
def test_valid_move_king():
    assert PieceRules.is_valid_move(
        "wK",
        0,0,
        1,1
    )


def test_invalid_move_king():
    assert not PieceRules.is_valid_move(
        "wK",
        0,0,
        2,2
    )


def test_valid_move_rook():
    assert PieceRules.is_valid_move(
        "wR",
        0,0,
        0,3
    )


def test_invalid_token_move():
    assert PieceRules.is_valid_move(
        ".",
        0,0,
        1,1
    ) == False      
def test_white_pawn_moves_up_one_square_empty():
    """חייל לבן יכול לזוז תא אחד קדימה למשבצת ריקה"""
    # שורה 4 לשורה 3 זה תנועה למעלה
    assert PieceRules.is_valid_move('wP', src_row=4, src_col=3, dst_row=3, dst_col=3, target_piece='.') is True

def test_white_pawn_cannot_move_up_if_blocked():
    """חייל לבן אינו יכול לזוז קדימה אם יש שם כלי (אינו יכול לתפוס קדימה)"""
    assert PieceRules.is_valid_move('wP', src_row=4, src_col=3, dst_row=3, dst_col=3, target_piece='bP') is False

def test_white_pawn_captures_diagonally():
    """חייל לבן יכול לתפוס כלי אויב באלכסון קדימה"""
    assert PieceRules.is_valid_move('wP', src_row=4, src_col=3, dst_row=3, dst_col=4, target_piece='bP') is True

def test_white_pawn_cannot_diagonal_move_if_empty():
    """חייל לבן אינו יכול לזוז באלכסון אם המשבצת ריקה"""
    assert PieceRules.is_valid_move('wP', src_row=4, src_col=3, dst_row=3, dst_col=4, target_piece='.') is False


# --- בדיקות עבור חייל שחור (bP) - נע למטה (Row גדל ב-1) ---

def test_black_pawn_moves_down_one_square_empty():
    """חייל שחור יכול לזוז תא אחד קדימה למטה למשבצת ריקה"""
    # שורה 1 לשורה 2 זה תנועה למטה
    assert PieceRules.is_valid_move('bP', src_row=1, src_col=3, dst_row=2, dst_col=3, target_piece='.') is True

def test_black_pawn_cannot_move_down_if_blocked():
    """חייל שחור אינו יכול לזוז קדימה אם יש שם כלי"""
    assert PieceRules.is_valid_move('bP', src_row=1, src_col=3, dst_row=2, dst_col=3, target_piece='wP') is False

def test_black_pawn_captures_diagonally_down():
    """חייל שחור יכול לתפוס כלי אויב באלכסון קדימה למטה"""
    assert PieceRules.is_valid_move('bP', src_row=1, src_col=3, dst_row=2, dst_col=2, target_piece='wP') is True


# --- בדיקות הגבלות כלליות לחיילים ---

def test_pawns_cannot_move_two_squares():
    """חיילים אינם יכולים לזוז שני תאים קדימה באיטרציה זו"""
    # לבן מנסה לקפוץ 2 תאים
    assert PieceRules.is_valid_move('wP', src_row=6, src_col=3, dst_row=4, dst_col=3, target_piece='.') is False
    # שחור מנסה לקפוץ 2 תאים
    assert PieceRules.is_valid_move('bP', src_row=1, src_col=3, dst_row=3, dst_col=3, target_piece='.') is False

def test_white_pawn_cannot_move_wrong_direction():
    """חייל לבן אינו יכול לזוז אחורה (למטה)"""
    assert PieceRules.is_valid_move('wP', src_row=4, src_col=3, dst_row=5, dst_col=3, target_piece='.') is False                  