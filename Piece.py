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
        """
        בודקת חוקיות מהלך כולל חוסמים בדרך ואכילת כלי אויב.
        """
        # 1. עמידה במקום אינה מהלך חוקי
        if start_row == end_row and start_col == end_col:
            return False

        # 2. שליפת הכלים בנקודת ההתחלה והסוף
        moving_piece = board.get_piece_at(start_row, start_col)
        target_piece = board.get_piece_at(end_row, end_col)
        
        if moving_piece == '.':
            return False
            
        piece_type = moving_piece[1]
        moving_color = moving_piece[0]

        # 3. בדיקה אם יעד התנועה מכיל כלי מאותו הצבע
        if target_piece != '.' and target_piece[0] == moving_color:
            return False

        # חישוב מרחקים
        dr = abs(end_row - start_row)
        dc = abs(end_col - start_col)

        # 4. בדיקת דפוס תנועה גיאומטרי וחוסמים בדרך לפי סוג הכלי
        if piece_type == 'K':      # מלך
            return dr <= 1 and dc <= 1
            
        elif piece_type == 'N':    # פרש (יכול לקפוץ מעל חוסמים, לכן אין בדיקת מסלול)
            return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)

        # עבור כלים שנעים למרחק (צריח, רץ, מלכה) - נבדוק חסימות בדרך
        elif piece_type in ['R', 'B', 'Q']:
            # בדיקת התאמה גיאומטרית בסיסית
            if piece_type == 'R' and not (dr == 0 or dc == 0):
                return False
            if piece_type == 'B' and not (dr == dc):
                return False
            if piece_type == 'Q' and not (dr == 0 or dc == 0 or dr == dc):
                return False

            # קביעת כיוון הצעדים (1, 0, או 1-)
            step_row = 0 if end_row == start_row else (1 if end_row > start_row else -1)
            step_col = 0 if end_col == start_col else (1 if end_col > start_col else -1)

            # סריקת המסלול (לא כולל נקודת ההתחלה ונקודת הסוף)
            current_row = start_row + step_row
            current_col = start_col + step_col

            while current_row != end_row or current_col != end_col:
                if board.get_piece_at(current_row, current_col) != '.':
                    return False  # נמצא חוסם בדרך!
                current_row += step_row
                current_col += step_col

            return True

        return False