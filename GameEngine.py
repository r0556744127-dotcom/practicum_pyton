from RuleEngine import RuleEngine


class GameEngine:
    """מנוע המשחק הראשי שמנהל את הסטייט הדינמי והזמן."""

    def __init__(self, board: 'MappBoard'):
        self.board = board
        self.rule_engine = RuleEngine(board)
        self.selected_cell = None
        self.game_clock_ms = 0

    def handle_click(self, x: int, y: int) -> None:
        coords = self.rule_engine.convert_pixel_to_cell(x, y)

        # לחיצה מחוץ ללוח מתעלמים
        if coords is None:
            return

        row, col = coords
        current_piece = self.board.get_piece_at(row, col)

        # אין כלי שנבחר עדיין
        if self.selected_cell is None:

            # אפשר לבחור רק כלי ולא תא ריק
            if current_piece != '.':
                self.selected_cell = (row, col)

            return

        # יש כלי שנבחר

        # לחיצה על כלי מאותו צבע -> החלפת בחירה
        if self.rule_engine.is_friendly(
                 (row, col),
                 self.selected_cell
        ):
            self.selected_cell = (row, col)
            return

        # בדיקת חוקי תנועה של הכלי
        if not self.rule_engine.is_valid_move(
                self.selected_cell,
                (row, col)
        ):
            self.selected_cell = None
            return

        # בדיקת חסימות בדרך (צריח, רץ, מלכה)
        if not self.rule_engine.is_path_clear(
                self.selected_cell,
                (row, col)
        ):
            self.selected_cell = None
            return

        # ביצוע ההזזה
        src_row, src_col = self.selected_cell

        piece = self.board.get_piece_at(src_row, src_col)

        self.board.set_piece_at(src_row, src_col, '.')
        self.board.set_piece_at(row, col, piece)

        # ניקוי בחירה
        self.selected_cell = None


    def handle_wait(self, ms: int) -> None:
        self.game_clock_ms += ms


    def create_snapshot(self) -> 'GameSnapshot':
        from GameSnapshot import GameSnapshot

        return GameSnapshot(
            self.board.get_raw_matrix(),
            self.game_clock_ms
        )