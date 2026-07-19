from dataclasses import dataclass
@dataclass(frozen=True)
class PieceSnapshot:
    """מצב ציור של כלי אחד ברגע נתון — לקריאה בלבד."""
    sprite: object
    x_px: int
    y_px: int
    row: int
    col: int


@dataclass(frozen=True)
class GameSnapshot:
    """צילום מצב מלא של הלוח לרגע אחד — כל מה שהציור צריך."""
    rows: int
    cols: int
    clock: int
    pieces: tuple
    score_text: str = ""
    moves_lines: tuple = ()
    game_over: bool = False
    selected: tuple = None 
    banner: str = None



def build_snapshot(board, piece_views, engine,
                   score_tracker=None, move_tracker=None,selected=None,banner=None) -> GameSnapshot:
    """בונה GameSnapshot מהמצב הנוכחי — קורא בלבד."""
    pieces = []
    for view in piece_views.values():
        pieces.append(PieceSnapshot(
            sprite=view.current_sprite(),
            x_px=view.x_px,
            y_px=view.y_px,
            row=view.row,
            col=view.col,
        ))

    score_text = ""
    if score_tracker is not None:
        s = score_tracker.score
        score_text = f"White: {s['w']}   Black: {s['b']}"

    moves_lines = ()
    if move_tracker is not None:
        moves_lines = tuple(move_tracker.moves[-10:])

    return GameSnapshot(
        rows=board.rows,
        cols=board.cols,
        clock=engine.arbiter.clock,
        pieces=tuple(pieces),
        score_text=score_text,
        moves_lines=moves_lines,
        game_over=engine.game_over,
        selected=selected,
        banner=banner,
    )


if __name__ == "__main__":
    import sys
    import os
    _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, _ROOT)
    sys.path.insert(0, os.path.join(_ROOT, "core"))

    from board_parser import BoardParser
    from game_controller import GameController
    from ui.piece_view import PieceView

    board, _ = BoardParser().parse(["Board:", "wP .", ". ."])
    controller = GameController(board)

    views = {(0, 0): PieceView(board.get_cell(0, 0), 0, 0)}
    for v in views.values():
        v.update_pixel_pos(controller.engine)

    snap = build_snapshot(board, views, controller.engine)
    assert snap.game_over is False
    print("snapshot OK")