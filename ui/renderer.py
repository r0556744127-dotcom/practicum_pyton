import cv2
import numpy as np
from img import Img
from ui.ui_config import BOARD_IMAGE

PANEL_WIDTH = 240
PANEL_COLOR = (40, 40, 40, 255)


class Renderer:
    """מצייר GameSnapshot: לוח + כלים + פאנל צד. לא מכיר מנוע/state."""

    def __init__(self, board_image: str = BOARD_IMAGE):
        self.board_image = board_image

    def render(self, snapshot):
        board_img = Img().read(self.board_image).img
        if board_img.shape[2] == 3:
            board_img = cv2.cvtColor(board_img, cv2.COLOR_BGR2BGRA)

        bh, bw = board_img.shape[:2]

        canvas = Img()
        canvas.img = np.zeros((bh, bw + PANEL_WIDTH, 4), dtype=board_img.dtype)
        canvas.img[:, :] = PANEL_COLOR          # רקע פאנל
        canvas.img[:, :bw] = board_img          # הדבקת הלוח משמאל

        for ps in snapshot.pieces:
            ps.sprite.draw_on(canvas, ps.x_px, ps.y_px)

        self._draw_panel(canvas, snapshot, bw)

        if snapshot.game_over:
            self._draw_game_over(canvas, bw, bh)

        return canvas

    def _draw_panel(self, canvas, snapshot, board_w):
        x = board_w + 15

        if snapshot.score_text:
            canvas.put_text("SCORE", x, 40, 0.7,
                            color=(0, 255, 0, 255), thickness=2)
            canvas.put_text(snapshot.score_text, x, 75, 0.6,
                            color=(255, 255, 255, 255), thickness=1)

        y = 130
        for line in snapshot.moves_lines:
            canvas.put_text(line, x, y, 0.45,
                            color=(200, 200, 200, 255), thickness=1)
            y += 24

    def _draw_game_over(self, canvas, board_w, board_h):
        canvas.put_text("GAME OVER", board_w // 2 - 180, board_h // 2, 1.6,
                        color=(0, 0, 255, 255), thickness=4)


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from board_parser import BoardParser
    from game_controller import GameController
    from ui.piece_view import PieceView
    from ui.game_snapshot import build_snapshot
    from ui.trackers import ScoreTracker

    board, _ = BoardParser().parse(["Board:", "wP wP", ". ."])
    controller = GameController(board)

    views = {}
    for r in range(board.rows):
        for c in range(board.cols):
            p = board.get_cell(r, c)
            if p is not None:
                v = PieceView(p, r, c)
                v.update_pixel_pos(controller.engine)
                views[(r, c)] = v

    score = ScoreTracker()
    score.update(controller.board)

    snap = build_snapshot(board, views, controller.engine, score)
    canvas = Renderer().render(snap)

    print("canvas shape:", canvas.img.shape)
    print("panel OK — press any key to close")
    canvas.show()