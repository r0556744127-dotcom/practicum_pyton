import cv2
from img import Img
from board_mapper import BoardMapper
from sprite_utils import sprite_path
from ui_config import BOARD_IMAGE, CELL_SIZE_PX


def make_white_transparent(img_obj, threshold=240):
    """הופך פיקסלים כמעט-לבנים לשקופים — פתרון זמני לספרייטי פיתוח."""
    if img_obj.img is None:
        return img_obj

    img = img_obj.img
    if len(img.shape) == 2 or img.shape[2] == 4:
        return img_obj

    # BGR (3 ערוצים) → BGRA (4 ערוצים עם שקיפות)
    bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # פיקסלים לבנים → שקופים
    white_mask = (
        (bgra[:, :, 0] > threshold) &
        (bgra[:, :, 1] > threshold) &
        (bgra[:, :, 2] > threshold)
    )
    bgra[white_mask, 3] = 0

    img_obj.img = bgra
    return img_obj


def draw_static_board(board):
    mapper = BoardMapper(CELL_SIZE_PX)

    bg = Img().read(BOARD_IMAGE)
    canvas = Img()
    canvas.img = bg.img.copy()   # רקע נקי!

    # הלוח הוא 3 ערוצים — ממירים ל-4 כדי ששקיפות תעבוד
    if canvas.img.shape[2] == 3:
        canvas.img = cv2.cvtColor(canvas.img, cv2.COLOR_BGR2BGRA)

    for row in range(board.rows):
        for col in range(board.cols):
            piece = board.get_cell(row, col)
            if piece is None:
                continue

            path = sprite_path(piece, "idle", 0)

            sprite = Img().read(path, size=(CELL_SIZE_PX, CELL_SIZE_PX), keep_aspect=True)
            make_white_transparent(sprite)   # מסיר רקע לבן

            x, y = mapper.to_pixel(row, col)
            sprite.draw_on(canvas, x, y)

    canvas.show()