class Piece:
    @staticmethod
    def is_valid(token: str) -> bool:
        if token == '.':
            return True
        if len(token) != 2:
            return False
        return token[0] in ['w', 'b'] and token[1] in ['K', 'Q', 'R', 'B', 'N', 'P']

    @staticmethod
    def is_legal_move(piece_type: str, start_row: int, start_col: int, end_row: int, end_col: int) -> bool:
        if start_row == end_row and start_col == end_col:
            return False

        dr = abs(end_row - start_row)
        dc = abs(end_col - start_col)
        
        if piece_type == 'K':      
            return dr <= 1 and dc <= 1
        elif piece_type == 'R':   
            return dr == 0 or dc == 0
        elif piece_type == 'B':   
            return dr == dc
        elif piece_type == 'Q':   
            return dr == 0 or dc == 0 or dr == dc
        elif piece_type == 'N':    
            return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)
            
        return False