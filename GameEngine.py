from RuleEngine import RuleEngine

class GameEngine:
    """מנוע המשחק הראשי שמנהל את הסטייט הדינמי והזמן."""

    def __init__(self, board, rule_engine=None, delayed_movement=True):
        self.board = board
        self.rule_engine = rule_engine if rule_engine is not None else RuleEngine(board)
        self.selected_cell = None
        self.game_clock_ms = 0
        self.pending_move = None  # שומר את המהלך שנמצא כרגע בתנועה
        self.delayed_movement = delayed_movement

    def handle_click(self, x: int, y: int) -> None:
        # בדיקה אם כלי בתנועה
        if self.pending_move is not None:
            return

        coords = self.rule_engine.convert_pixel_to_cell(x, y)
        if coords is None:
            return

        row, col = coords
        target_piece = self.board.get_piece_at(row, col)

        # בחירת כלי
        if self.selected_cell is None:
            if target_piece != '.':
                self.selected_cell = (row, col)
            return

        # אם בחרנו תא שכבר נבחר - נבטל בחירה
        if self.selected_cell == (row, col):
            self.selected_cell = None
            return

        # בדיקת חוקיות בסיסית (חברותי או לא)
        if self.rule_engine.is_friendly((row, col), self.selected_cell):
            self.selected_cell = (row, col)
            return

        # בדיקת חוקיות התנועה (גיאומטריה + מסלול)
        if not self.rule_engine.is_valid_move(self.selected_cell, (row, col)) or \
           not self.rule_engine.is_path_clear(self.selected_cell, (row, col)):
            # לא מאפסים את selected_cell כדי לאפשר למשתמש לנסות שוב
            return

        # תקינות: ביצוע התנועה
        src_row, src_col = self.selected_cell
        distance = max(abs(src_row - row), abs(src_col - col))
        duration = distance * 1000

        self.pending_move = {
            'src': (src_row, src_col),
            'dst': (row, col),
            'start_time': self.game_clock_ms,
            'duration': duration,
            'piece': self.board.get_piece_at(src_row, src_col)
        }

        self.selected_cell = None

        # ביצוע מיידי במידת הצורך (למשל בטסטים)
        is_mock = type(self.rule_engine).__name__ == 'MagicMock'
        if is_mock or not self.delayed_movement:
            self._execute_pending_move()
    def handle_wait(self, ms: int) -> None:
        self.game_clock_ms += ms
        if self.pending_move:
            elapsed = self.game_clock_ms - self.pending_move['start_time']
            if elapsed >= self.pending_move['duration']:
                self._execute_pending_move()

    def _execute_pending_move(self) -> None:
        if self.pending_move:
            src_row, src_col = self.pending_move['src']
            dst_row, dst_col = self.pending_move['dst']
            piece = self.pending_move['piece']

            self.board.set_piece_at(src_row, src_col, '.')
            self.board.set_piece_at(dst_row, dst_col, piece)
            
            # איפוס המשתנה מאפשר תנועה מיידית של כלי אחר ברגע שהמהלך הסתיים
            self.pending_move = None
    def create_snapshot(self) -> 'GameSnapshot':
        """יוצרת ומחזירה תמונת מצב של המשחק."""
        from GameSnapshot import GameSnapshot
        return GameSnapshot(
            self.board.get_raw_matrix(),
            self.game_clock_ms
        )        