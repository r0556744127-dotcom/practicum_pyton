import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import cv2
from board_parser import BoardParser
from game_controller import GameController
from ui.ui_config import WINDOW_NAME
from ui.ui_helpers import build_board_canvas, sync_piece_views
STARTING_BOARD = [
    "Board:",
    "bR bN bB bQ bK bB bN bR",
    "bP bP bP bP bP bP bP bP",
    ". . . . . . . .",
    ". . . . . . . .",
    ". . . . . . . .",
    ". . . . . . . .",
    "wP wP wP wP wP wP wP wP",
    "wR wN wB wQ wK wB wN wR",

]


def draw_click_marks(canvas, marks):
    for (x, y) in marks:
        cv2.drawMarker(
            canvas.img, (x, y), (0, 0, 255, 255),
            markerType=cv2.MARKER_CROSS,
            markerSize=20,
            thickness=2,
        )


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        controller = param["controller"]
        marks = param["marks"]

        controller.click(x, y)
        marks.append((x, y))
        print(f"click at ({x}, {y})")


def run_ui():
    parser = BoardParser()
    board, _ = parser.parse(STARTING_BOARD)
    controller = GameController(board)
    click_marks = []

    cv2.namedWindow(WINDOW_NAME)
    prev = time.time()
    piece_views = {}

    while True:
        now = time.time()
        dt_ms = max(1, int((now - prev) * 1000))
        prev = now

        controller.wait(dt_ms)

        piece_views = sync_piece_views(controller.board, piece_views, controller)
        for view in piece_views.values():
            view.update(dt_ms)

        canvas = build_board_canvas(controller.board, piece_views)
        draw_click_marks(canvas, click_marks)

        cv2.setMouseCallback(WINDOW_NAME, on_mouse, {
            "canvas": canvas,
            "controller": controller,
            "marks": click_marks,
        })
        cv2.imshow(WINDOW_NAME, canvas.img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_ui()