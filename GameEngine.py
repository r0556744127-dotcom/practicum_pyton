from RuleEngine import RuleEngine

class GameEngine:
    """מנוע המשחק הראשי שמנהל את הסטייט הדינמי והזמן."""

    def __init__(self, board, rule_engine=None, delayed_movement=True):
        self.board = board
        self.rule_engine = rule_engine if rule_engine is not None else RuleEngine(board)
        self.selected_cell = None
        self.game_clock_ms = 0
        self.pending_move = None
        self.delayed_movement = delayed_movement
        self.game_over = False

    def handle_click(self, x: int, y: int) -> None:
        if self.game_over or self.pending_move is not None:
            return

        coords = self.rule_engine.convert_pixel_to_cell(x, y)
        if coords is None:
            self.selected_cell = None
            return

        row, col = coords
        target_piece = self.board.get_piece_at(row, col)

        if self.selected_cell is None:
            if target_piece != '.':
                self.selected_cell = (row, col)
            return

        if self.selected_cell == (row, col):
            self.selected_cell = None
            return
        
        if self.rule_engine.is_friendly((row, col), self.selected_cell):
            self.selected_cell = (row, col)
            return

        # --- הוספת הבדיקה לזיהוי הכאת מלך ---
        is_king_capture = ('K' in str(target_piece))
        
        # אם זה לא הכאת מלך, נמשיך לבדוק חוקיות רגילה
        if not is_king_capture:
            if not self.rule_engine.is_valid_move(self.selected_cell, (row, col)) or \
               not self.rule_engine.is_path_clear(self.selected_cell, (row, col)):
                return
        # -----------------------------------

        src_row, src_col = self.selected_cell
        self.pending_move = {
            'src': (src_row, src_col),
            'dst': (row, col),
            'start_time': self.game_clock_ms,
            'duration': max(abs(src_row - row), abs(src_col - col)) * 1000,
            'piece': self.board.get_piece_at(src_row, src_col)
        }
        self.selected_cell = None

        if not self.delayed_movement:
            self._execute_pending_move()
    def handle_wait(self, ms: int) -> None:
        self.game_clock_ms += ms
        if self.pending_move:
            if self.game_clock_ms - self.pending_move['start_time'] >= self.pending_move['duration']:
                self._execute_pending_move()

    def _execute_pending_move(self) -> None:
        if not self.pending_move:
            return

        src = self.pending_move['src']
        dst = self.pending_move['dst']
        piece = self.pending_move['piece']
        
        # בדיקה אם המהלך תופס מלך לפני ביצוע השינוי בלוח
        target = self.board.get_piece_at(dst[0], dst[1])
        if target is not None and 'K' in str(target):
            self.game_over = True
        
        # ביצוע המהלך
        self.board.set_piece_at(src[0], src[1], '.')
        self.board.set_piece_at(dst[0], dst[1], piece)
        
        self.pending_move = None
    def create_snapshot(self) -> 'GameSnapshot':
        from GameSnapshot import GameSnapshot
        return GameSnapshot(self.board.get_raw_matrix(), self.game_clock_ms)