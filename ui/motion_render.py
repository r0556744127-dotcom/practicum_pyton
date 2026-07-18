import sys
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))

from motion import Motion
from ui.ui_config import CELL_SIZE_PX

# זה הלב של "חלק" — מעבר הדרגתי ולא קפיצה.
# מחזיר נקודה בין a ל-b לפי אחוז t:

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

# "כובל" את t לטווח [0, 1].


def clamp01(t: float) -> float:
    if t < 0.0:
        return 0.0
    if t > 1.0:
        return 1.0
    return t

# "אם כלי נמצא בשורה row ועמודה col — באיזה פיקסל על המסך מתחילה המשבצת שלו?"
def _cell_top_left(row: int, col: int) -> tuple[int, int]:
    return col * CELL_SIZE_PX, row * CELL_SIZE_PX

# כמה אחוז מהדרך עבר
def motion_progress(motion, clock: int) -> float:
    distance = max(abs(motion.to_row - motion.from_row),
                   abs(motion.to_col - motion.from_col))
    duration = distance * Motion.TIME_PER_CELL_MS
    if duration == 0:
        return 1.0
    start_time = motion.arrival_time - duration
    t = (clock - start_time) / duration
    return clamp01(t)


def motion_pixel_pos(motion, clock: int,
                     sprite_w: int, sprite_h: int) -> tuple[int, int]:
    t = motion_progress(motion, clock)

    from_x, from_y = _cell_top_left(motion.from_row, motion.from_col)
    to_x, to_y = _cell_top_left(motion.to_row, motion.to_col)

    from_x += (CELL_SIZE_PX - sprite_w) // 2
    from_y += (CELL_SIZE_PX - sprite_h) // 2
    to_x += (CELL_SIZE_PX - sprite_w) // 2
    to_y += (CELL_SIZE_PX - sprite_h) // 2

    x = int(lerp(from_x, to_x, t))
    y = int(lerp(from_y, to_y, t))
    return x, y


if __name__ == "__main__":
    # בדיקות 6.2
    assert lerp(600, 500, 0.5) == 550
    assert clamp01(1.5) == 1.0

    # בדיקת 6.3 — חייל שחור זז למטה משבצת אחת
    from board_parser import BoardParser
    from game_engine import GameEngine

    board, _ = BoardParser().parse(["Board:", "bP .", ". .", ". ."])
    engine = GameEngine(board, 1000)

    result = engine.request_move(0, 0, 1, 0)
    assert result == "scheduled", f"move not scheduled: {result}"

    m = engine.arbiter.pending_motions[0]
    w, h = 80, 80

    t0, (x0, y0) = motion_progress(m, 0), motion_pixel_pos(m, 0, w, h)
    t1, (x1, y1) = motion_progress(m, 500), motion_pixel_pos(m, 500, w, h)
    t2, (x2, y2) = motion_progress(m, 1000), motion_pixel_pos(m, 1000, w, h)

    print(f"clock=0:    t={t0}, pos=({x0},{y0})")
    print(f"clock=500:  t={t1}, pos=({x1},{y1})")
    print(f"clock=1000: t={t2}, pos=({x2},{y2})")

    assert t0 == 0.0
    assert t1 == 0.5
    assert t2 == 1.0
    assert y0 < y1 < y2   # שחור יורד (שורה 0 → שורה 1)
    print("6.3 OK")