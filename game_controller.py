from board_mapper import BoardMapper
from board_view import BoardRenderer
from game_engine import GameEngine

# החיבור בין הממשק (המשתמש) לבין המנוע.
class GameController:

    CELL_SIZE = 100
    JUMP_DURATION_MS = 1000
    

    def __init__(self, board, mapper=None, engine=None):
        """mapper and engine are optional Dependency Injection points
        (tests can supply fakes/stubs here instead of monkeypatching);
        production code omits them and gets the real collaborators."""
        self.board = board
        self.mapper = mapper if mapper is not None else BoardMapper(self.CELL_SIZE)
        self.engine = engine if engine is not None else GameEngine(board, self.JUMP_DURATION_MS)
        self.selected = None

    def click(self, x, y):
        if self.engine.game_over:
            return
        row, col = self.mapper.to_cell(x, y)

        if not self.board.is_inside(row, col):
            return

        token = self.board.get_cell(row, col)

        if self.selected is None:
            if token is None:
                return
            if self.engine.has_pending_move_from(row, col):
                return
            if self.engine.is_airborne(row, col):
                return
            self.selected = (row, col)
            return

        selected_row, selected_col = self.selected
        selected_piece = self.board.get_cell(selected_row, selected_col)

        if token is not None and token.color == selected_piece.color:
            self.selected = (row, col)
            return

        result = self.engine.request_move(selected_row, selected_col, row, col)
        if result == "invalid":
            # Keep the current selection so the user can try again.
            return

        self.selected = None

    def jump(self, x, y):
        if self.engine.game_over:
            return

        row, col = self.mapper.to_cell(x, y)

        if not self.board.is_inside(row, col):
            return

        self.engine.request_jump(row, col)

    def wait(self, ms):
        self.engine.advance_time(ms)

    def print_board(self):
        BoardRenderer.render(self.board)
