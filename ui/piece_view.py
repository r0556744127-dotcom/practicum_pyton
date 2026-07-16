from ui.animation import Animation
from piece import Piece


class PieceView:
    """ייצוג גרפי של כלי אחד על הלוח."""

    def __init__(self, piece: Piece, row: int, col: int):
        self.piece = piece
        self.row = row
        self.col = col
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