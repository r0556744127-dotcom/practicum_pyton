import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from piece import Piece
from ui.animation import Animation


def main():
    pawn = Piece("w", "P")
    anim = Animation(pawn, "idle")

    print("piece:       ", pawn)
    print("state:       ", anim.state_name)
    print("frame_count: ", anim.frame_count())
    print("fps:         ", anim.fps)
    print("is_loop:     ", anim.is_loop)
    print("next_state:  ", anim.next_state)
    print("speed_m/s:   ", anim.speed_m_per_sec)
    print("current idx: ", anim.index)

    # מציג פריים ראשון (שלב 4.4 יוסיף לולאה)
    anim.current().show()


if __name__ == "__main__":
    main()