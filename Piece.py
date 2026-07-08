class Piece:
    @staticmethod
    def is_valid(token: str) -> bool:
        if token == '.':
            return True
        if len(token) != 2:
            return False
        return token[0] in ['w', 'b'] and token[1] in ['K', 'Q', 'R', 'B', 'N', 'P']

    @staticmethod
    def is_legal_move(board, start_row: int, start_col: int, end_row: int, end_col: int) -> bool:
        if start_row == end_row and start_col == end_col:
            return False

        moving_piece = board.get_piece_at(start_row, start_col)
        target_piece = board.get_piece_at(end_row, end_col)
        
        if moving_piece == '.':
            return False
            
        piece_type = moving_piece[1]
        moving_color = moving_piece[0]

        # חוק כללי: לא נוחתים על כלי מאותו צבע
        if target_piece != '.' and target_piece[0] == moving_color:
            return False

        row_diff = end_row - start_row
        col_diff = end_col - start_col
        dr = abs(row_diff)
        dc = abs(col_diff)

        # לוגיקת חייל (Pawn) מעודכנת
        if piece_type == 'P':
            # כיוון תנועה ושורת התחלה לפי צבע הכלי
            valid_direction = -1 if moving_color == 'w' else 1
            start_row_baseline = 6 if moving_color == 'w' else 1
            
            # 1. צעד אחד ישר קדימה (הנתיב חייב להיות פנוי)
            if col_diff == 0 and row_diff == valid_direction:
                return target_piece == '.'
                
            # 2. צעד כפול משורת ההתחלה (הנתיב והיעד חייבים להיות פנויים)
            if col_diff == 0 and start_row == start_row_baseline and row_diff == 2 * valid_direction:
                intermediate_row = start_row + valid_direction
                return (board.get_piece_at(intermediate_row, start_col) == '.' and 
                        target_piece == '.')

            # 3. אכילה באלכסון (צעד אחד קדימה, אחד הצידה - רק אם יש כלי יריב)
            if dc == 1 and row_diff == valid_direction:
                return target_piece != '.' and target_piece[0] != moving_color

            return False

        # מלך
        if piece_type == 'K':
            return dr <= 1 and dc <= 1
            
        # פרש
        if piece_type == 'N':
            return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)

        # צריח, רץ, מלכה
        if piece_type in ['R', 'B', 'Q']:
            if piece_type == 'R' and not (dr == 0 or dc == 0):
                return False
            if piece_type == 'B' and not (dr == dc):
                return False
            if piece_type == 'Q' and not (dr == 0 or dc == 0 or dr == dc):
                return False

            step_row = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
            step_col = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)

            current_row = start_row + step_row
            current_col = start_col + step_col

            while current_row != end_row or current_col != end_col:
                if board.get_piece_at(current_row, current_col) != '.':
                    return False
                current_row += step_row
                current_col += step_col

            return True

        return False