from collections import Counter
from ui.ui_config import CAPTURE_POINTS
class ScoreTracker:
    """סופר לכידות ע"י השוואת מלאי כלים בין פריימים. Observer בצד ה-UI."""
    def __init__(self):
        self._prev = None
        self.score = {"w": 0, "b": 0}
    def update(self, board) -> None:
        curr = self._inventory(board)
        if self._prev is not None:
            disappeared = self._prev - curr
            appeared = curr - self._prev
            for (color, kind), n in disappeared.items():
                # הכתרה: חייל "נעלם" אבל כלי אחר מאותו צבע מופיע — לא לכידה
                if kind == "P" and any(c == color and k != "P"
                                       for (c, k) in appeared):
                    continue
                opponent = "w" if color == "b" else "b"
                self.score[opponent] += CAPTURE_POINTS.get(kind, 0) * n
        self._prev = curr
    def _inventory(self, board) -> Counter:
        c = Counter()
        for row in range(board.rows):
            for col in range(board.cols):
                p = board.get_cell(row, col)
                if p is not None:
                    c[(p.color, p.kind)] += 1
        return c
class MoveTracker:
    """עוקב אחרי מהלכים ורושם כל אחד פעם אחת. Observer בצד ה-UI."""

    def __init__(self):
        self._seen = set()
        self.moves = []

    def update(self, engine) -> None:
        for m in engine.arbiter.pending_motions:
            key = (m.from_row, m.from_col, m.to_row, m.to_col, m.arrival_time)
            if key not in self._seen:
                self._seen.add(key)
                self.moves.append(self._format(m))

    def _format(self, m) -> str:
        color = m.color or "?"
        return f"{color}: ({m.from_row},{m.from_col})->({m.to_row},{m.to_col})"