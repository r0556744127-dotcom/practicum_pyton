import sys
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))

from ui.animation import Animation
from piece import Piece
from ui.ui_config import CELL_SIZE_PX
from ui.motion_render import motion_pixel_pos


class PieceView:
    """ייצוג גרפי של כלי אחד על הלוח."""

    def __init__(self, piece: Piece, row: int, col: int):
        self.piece = piece
        self.row = row
        self.col = col
        self.x_px = col * CELL_SIZE_PX
        self.y_px = row * CELL_SIZE_PX
        self.state_name = "idle"
        self.anim = Animation(piece, "idle")

    def set_state(self, state_name: str) -> None:
        """מחליף state וטוען Animation חדש."""
        if state_name == self.state_name:
            return
        self.state_name = state_name
        self.anim = Animation(self.piece, state_name)

    def update(self, dt_ms: int) -> None:
        """מקדם אנימציה + מעבר אוטומטי כשאנימציה נגמרת."""
        if self.state_name == "idle":
            return  # כלי עומד — לא מחליף פריימים

        self.anim.update(dt_ms)

        if self.anim.finished:
            nxt = self.anim.next_state
            if nxt:
                self.set_state(nxt)

    def current_sprite(self):
        return self.anim.current()

    def _find_motion(self, engine):
        """מחפש מהלך פעיל שיוצא מהמשבצת של הכלי."""
        for m in engine.arbiter.pending_motions:
            if m.from_row == self.row and m.from_col == self.col:
                return m
        return None

    def update_pixel_pos(self, engine) -> None:
        """מעדכן x_px, y_px — בין משבצות אם בתנועה, אחרת ממורכז."""
        sprite = self.current_sprite()
        h, w = sprite.img.shape[:2]

        motion = self._find_motion(engine)

        if motion is not None:
            self.x_px, self.y_px = motion_pixel_pos(
                motion, engine.arbiter.clock, w, h)
        else:
            x = self.col * CELL_SIZE_PX + (CELL_SIZE_PX - w) // 2
            y = self.row * CELL_SIZE_PX + (CELL_SIZE_PX - h) // 2
            self.x_px = x
            self.y_px = y


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from piece import Piece

    view = PieceView(Piece("w", "P"), row=6, col=0)
    print("row,col:", view.row, view.col)
    print("x_px,y_px:", view.x_px, view.y_px)
    assert view.x_px == 0
    assert view.y_px == 600
    print("6.4 OK")