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

    def handle_click(self, x: int, y: int):
        if self.game_over:
            return

        cell = self.rule_engine.convert_pixel_to_cell(x, y)
        if not cell: return
        row, col = cell
        target_piece = self.board.get_piece_at(row, col)

        if self.selected_cell:
            src_row, src_col = self.selected_cell
            piece = self.board.get_piece_at(src_row, src_col)
            
            if self.rule_engine.is_valid_move(piece, src_row, src_col, row, col, target_piece):
                # ביצוע הזזה
                if 'K' in target_piece:
                    self.game_over = True
                
                self.board.set_piece_at(row, col, piece)
                self.board.set_piece_at(src_row, src_col, '.')
                
                # הכתרה
                if piece[1] == 'P' and (row == 0 or row == 7):
                    self.board.set_piece_at(row, col, piece[0] + 'Q')
                
                self.selected_cell = None
            else:
                # החלפת בחירה אם לחצו על כלי אחר
                self.selected_cell = (row, col) if target_piece != '.' else None
        else:
            if target_piece != '.':
                self.selected_cell = (row, col)
    def handle_wait(self, ms: int) -> None:
        self.game_clock_ms += ms
        if self.pending_move:
            if self.game_clock_ms - self.pending_move['start_time'] >= self.pending_move['duration']:
                self._execute_pending_move()

    
    def _execute_pending_move(self) -> None:
        if not self.pending_move:
            return

        src, dst, piece = self.pending_move['src'], self.pending_move['dst'], self.pending_move['piece']

        # 1. בדקי אם יש מלך ביעד לפני הזזה
        target = self.board.get_piece_at(dst[0], dst[1])
        if target is not None and 'K' in str(target):
            self.game_over = True

        # 2. הכתרה
        final_piece = piece
        if 'P' in piece:
            if (piece[0] == 'w' and dst[0] == 0) or (piece[0] == 'b' and dst[0] == 7):
                final_piece = f"{piece[0]}Q"

        # 3. ביצוע ההזזה בפועל
        self.board.set_piece_at(src[0], src[1], '.')
        self.board.set_piece_at(dst[0], dst[1], final_piece)

        self.pending_move = None

    def create_snapshot(self) -> 'GameSnapshot':
        from GameSnapshot import GameSnapshot
        return GameSnapshot(self.board.get_raw_matrix(), self.game_clock_ms)
   