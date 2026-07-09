from PieceRules import PieceRules
from MappBoard import MappBoard


class RuleEngine:

    CELL_SIZE = 100

    def __init__(self, board: MappBoard):
        self.board = board


    def is_valid_move(self, src, dst):

        src_row, src_col = src
        dst_row, dst_col = dst

        piece = self.board.get_piece_at(src_row, src_col)

        if piece == '.':
            return False

        return PieceRules.is_valid_move(
            piece,
            src_row,
            src_col,
            dst_row,
            dst_col
        )


    def convert_pixel_to_cell(self, x, y):

        rows, cols = self.board.get_dimensions()

        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if 0 <= row < rows and 0 <= col < cols:
            return row, col

        return None


    def is_friendly(self, cell_a, cell_b):

        if cell_a is None or cell_b is None:
            return False

        p1 = self.board.get_piece_at(
            cell_a[0],
            cell_a[1]
        )

        p2 = self.board.get_piece_at(
            cell_b[0],
            cell_b[1]
        )

        if p1 == '.' or p2 == '.':
            return False

        return p1[0] == p2[0]


    def is_path_clear(self, src, dst):

        src_row, src_col = src
        dst_row, dst_col = dst

        piece = self.board.get_piece_at(
            src_row,
            src_col
        )

        if piece == '.':
            return False


        # פרש לא צריך בדיקת דרך
        if piece[1] == 'N':
            return True


        row_step = (dst_row > src_row) - (dst_row < src_row)
        col_step = (dst_col > src_col) - (dst_col < src_col)


        row = src_row + row_step
        col = src_col + col_step


        while (row, col) != (dst_row, dst_col):

            if self.board.get_piece_at(row, col) != '.':
                return False

            row += row_step
            col += col_step


        return True