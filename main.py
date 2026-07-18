import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "core"))
from board_parser import BoardParser
from commands import parse_command
from game_controller import GameController
import cv2
from img import Img
# חישוב הנתיב המוחלט של תיקיית הפרויקט שבה נמצא main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# בניית נתיב מוחלט לתמונה - תמיד יעבוד, לא משנה מאיפה מריצים
Logo_path = os.path.join(BASE_DIR, "pieces", "QW", "states", "jump", "sprites", "2.png")

def run(lines=None):
    """Testable entry point: lines is an optional DI point (a list of
    input strings) so tests can drive the whole pipeline without
    monkeypatching stdin. main() calls this with no arguments, which
    reads from stdin exactly as before."""
    parser = BoardParser()

    try:
        board, command_lines = parser.parse(lines)
        controller = GameController(board)

        for line in command_lines:
            command = parse_command(line)
            if command is not None:
                command.execute(controller)

    except ValueError as e:
        print(f"ERROR {e}")


# def main():  # pragma: no cover
#     # Thin CLI wrapper around run() that reads real stdin - exercised by
#     # the real subprocess test in test_main.py, not monkeypatching.
#     run()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    # בדיקה האם אנחנו מריצים בדיקות (pytest)
    is_testing = os.environ.get("IS_TESTING") == "1"
    # טעינת התמונות תתבצע רק אם אנחנו לא בבדיקה
    if not is_testing:
        background = os.path.join(BASE_DIR, "board.png")
        logo = os.path.join(BASE_DIR, "pieces", "QW", "states", "jump", "sprites", "5.png")
       
        canvas = Img().read(background)
        piece = Img().read(logo, size=(100, 100), keep_aspect=True, interpolation=cv2.INTER_AREA)
        h, w = canvas.img.shape[:2]
        canvas.put_text("Demo", h // 2, w // 2, 3.0, color=(255, 0, 0, 255), thickness=5)
        piece.draw_on(canvas, 50, 50)
        canvas.show()
    
    # ה-run() תמיד ירוץ
    run()
if __name__ == "__main__":
    main()
