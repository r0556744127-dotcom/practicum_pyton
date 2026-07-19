from ui.ui_config import CAPTURE_POINTS


class ScoreTracker:
    """סופר לכידות ע"י האזנה לאירוע piece_captured מה-Bus."""

    def __init__(self):
        self.score = {"w": 0, "b": 0}

    def on_capture(self, data):
        """מופעל ע"י ה-Bus כשכלי נלכד. data = {"piece": "bQ", "by": "w", ...}"""
        kind = data["piece"][1]          # "bQ" -> "Q" (התו השני הוא סוג הכלי)
        by = data["by"]                  # מי לכד: "w" או "b"
        self.score[by] += CAPTURE_POINTS.get(kind, 0)


class MoveTracker:
    """רושם מהלכים ע"י האזנה לאירוע move_made מה-Bus."""

    def __init__(self):
        self.moves = []

    def on_move(self, data):
        """מופעל ע"י ה-Bus כשמתבצע מהלך. data = {"from":(r,c), "to":(r,c), "color":"w"}"""
        frm = data["from"]
        to = data["to"]
        color = data["color"]
        self.moves.append(f"{color}: {frm}->{to}")
