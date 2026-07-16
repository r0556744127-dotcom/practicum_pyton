import sys
import os
import time
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from piece import Piece
from ui.animation import Animation


def main():
    anim = Animation(Piece("w", "P"), "idle")

    cv2.namedWindow("Anim Demo")
    prev = time.time()

    while True:
        now = time.time()
        dt_ms = max(1, int((now - prev) * 1000))
        prev = now

        anim.update(dt_ms)

        cv2.imshow("Anim Demo", anim.current().img)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()