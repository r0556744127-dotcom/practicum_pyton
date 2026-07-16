import cv2
from img import Img
from board_mapper import BoardMapper
from ui.sprite_utils import sprite_path
# from ui.animation import Animation
from ui.ui_config import BOARD_IMAGE, CELL_SIZE_PX
from ui.piece_view import PieceView

# def sync_piece_anims(board, anims: dict) -> dict:
#     new_anims = {}
#     for row in range(board.rows):
#         for col in range(board.cols):
#             piece = board.get_cell(row, col)
#             if piece is None:
#                 continue
#             key = (row, col)
#             if key in anims:
#                 new_anims[key] = anims[key]
#             else:
#                 new_anims[key] = Animation(piece, "idle")
#     return new_anims
# # מצייר לוח + שקיפות
def make_white_transparent(img_obj, threshold=240):

    """הופך פיקסלים כמעט-לבנים לשקופים — פתרון זמני לספרייטי פיתוח."""
    if img_obj.img is None:
        return img_obj

    img = img_obj.img
    if len(img.shape) == 2 or img.shape[2] == 4:
        return img_obj

    bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    white_mask = (
        (bgra[:, :, 0] > threshold) &
        (bgra[:, :, 1] > threshold) &
        (bgra[:, :, 2] > threshold)
    )
    bgra[white_mask, 3] = 0

    img_obj.img = bgra
    return img_obj


def build_board_canvas(board, piece_views=None):
    """בונה תמונת לוח ומחזיר canvas — בלי show()."""
    mapper = BoardMapper(CELL_SIZE_PX)

    bg = Img().read(BOARD_IMAGE)
    canvas = Img()
    canvas.img = bg.img.copy()

    if canvas.img.shape[2] == 3:
        canvas.img = cv2.cvtColor(canvas.img, cv2.COLOR_BGR2BGRA)

    for row in range(board.rows):
        for col in range(board.cols):
            piece = board.get_cell(row, col)
            if piece is None:
                continue

            if piece_views and (row, col) in piece_views:
                sprite = piece_views[(row, col)].current_sprite()
            else:
                path = sprite_path(piece, "idle", 0)
                sprite = Img().read(path, size=(CELL_SIZE_PX, CELL_SIZE_PX), keep_aspect=True)
                make_white_transparent(sprite)

            x, y = mapper.to_pixel(row, col)
            h, w = sprite.img.shape[:2]
            x += (CELL_SIZE_PX - w) // 2
            y += (CELL_SIZE_PX - h) // 2
            sprite.draw_on(canvas, x, y)

    return canvas

def draw_static_board(board):
    """שלב 1 — מציג לוח סטטי פעם אחת."""
    build_board_canvas(board).show()
def _occupied_cells(board):
    cells = []
    for row in range(board.rows):
        for col in range(board.cols):
            piece = board.get_cell(row, col)
            if piece is not None:
                cells.append((row, col, piece))
    return cells
def _update_view_state(view: PieceView, engine, row: int, col: int) -> None:
    """מחליט איזה state ויזואלי להציג — לפי מצב המנוע."""
    # מנוחה — תן לאנימציה להסתיים
    if view.state_name in ("long_rest", "short_rest") and not view.anim.finished:
        return
    if engine.is_airborne(row, col):
        if view.state_name != "jump":
            view.set_state("jump")
        return
    if engine.has_pending_move_from(row, col):
        if view.state_name != "move":
            view.set_state("move")
        return
    if view.state_name == "move":
        view.set_state("long_rest")
        return
    if view.state_name == "jump":
        view.set_state("short_rest")
        return
def sync_piece_views(board, views: dict, controller) -> dict:
    engine = controller.engine
    occupied = {(r, c) for r, c, _ in _occupied_cells(board)}
    leftover = {k: v for k, v in views.items() if k not in occupied}
    new_views = {}
    for row, col, piece in _occupied_cells(board):
        key = (row, col)
        if key in views:
            view = views[key]
            view.row = row
            view.col = col
            view.piece = piece
        elif leftover:
            old_key, view = leftover.popitem()
            view.row = row
            view.col = col
            view.piece = piece
        else:
            view = PieceView(piece, row, col)
        _update_view_state(view, engine, row, col)
        new_views[key] = view
    return new_views    