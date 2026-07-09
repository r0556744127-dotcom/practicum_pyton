class PieceRules:
    """אחראית על חוקי התגים והתנועה התיאורטיים של הכלים."""

    VALID_TOKENS = {
        '.',
        'wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
        'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'
    }

    @staticmethod
    def is_valid_token(token: str) -> bool:
        return token in PieceRules.VALID_TOKENS


    @staticmethod
    def can_king_move(src_row, src_col, dst_row, dst_col):
        dr = abs(dst_row - src_row)
        dc = abs(dst_col - src_col)

        return dr <= 1 and dc <= 1 and (dr != 0 or dc != 0)


    @staticmethod
    def can_rook_move(src_row, src_col, dst_row, dst_col):
        return src_row == dst_row or src_col == dst_col


    @staticmethod
    def can_bishop_move(src_row, src_col, dst_row, dst_col):
        return abs(dst_row - src_row) == abs(dst_col - src_col)


    @staticmethod
    def can_queen_move(src_row, src_col, dst_row, dst_col):
        return (
            src_row == dst_row or
            src_col == dst_col or
            abs(dst_row - src_row) == abs(dst_col - src_col)
        )


    @staticmethod
    def can_knight_move(src_row, src_col, dst_row, dst_col):
        dr = abs(dst_row - src_row)
        dc = abs(dst_col - src_col)

        return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)


    @staticmethod
    def is_valid_move(piece, src_row, src_col, dst_row, dst_col):

        if piece == '.':
            return False

        piece_type = piece[1]

        if piece_type == 'K':
            return PieceRules.can_king_move(
                src_row, src_col, dst_row, dst_col
            )

        if piece_type == 'R':
            return PieceRules.can_rook_move(
                src_row, src_col, dst_row, dst_col
            )

        if piece_type == 'B':
            return PieceRules.can_bishop_move(
                src_row, src_col, dst_row, dst_col
            )

        if piece_type == 'Q':
            return PieceRules.can_queen_move(
                src_row, src_col, dst_row, dst_col
            )

        if piece_type == 'N':
            return PieceRules.can_knight_move(
                src_row, src_col, dst_row, dst_col
            )

        return False