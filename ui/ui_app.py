import sys
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))
import time
import cv2
from board_parser import BoardParser
from game_controller import GameController
from event_bus import EventBus
from ui.ui_config import WINDOW_NAME
from ui.ui_helpers import sync_piece_views
from ui.renderer import Renderer
from ui.game_snapshot import build_snapshot
from ui.trackers import MoveTracker, ScoreTracker
from ui.sound_player import SoundPlayer
from ui.banner import BannerEffect
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


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        controller = param["controller"]
        controller.click(x, y)
        print(f"click at ({x}, {y})")


def run_ui():
    parser = BoardParser()
    board, _ = parser.parse(STARTING_BOARD)

    # יצירת ה-Bus ורישום המאזינים (Pub/Sub)
    bus = EventBus()
    score_tracker = ScoreTracker()
    move_tracker = MoveTracker()
    sound = SoundPlayer()
    banner = BannerEffect()
    bus.subscribe("piece_captured", score_tracker.on_capture)
    bus.subscribe("move_made", move_tracker.on_move)
    bus.subscribe("game_over", sound.on_game_over)
    bus.subscribe("game_started", sound.on_game_started)
    bus.subscribe("game_started", banner.on_game_started)
    bus.subscribe("move_made", sound.on_move)
    bus.subscribe("piece_captured", sound.on_capture)
    # מעבירים את ה-Bus למנוע דרך ה-controller
    controller = GameController(board, bus=bus)

    cv2.namedWindow(WINDOW_NAME)
    prev = time.time()
    piece_views = {}
    renderer = Renderer()

    bus.publish("game_started", {})

    while True:
        now = time.time()
        dt_ms = max(1, int((now - prev) * 1000))
        prev = now

        controller.wait(dt_ms)

        piece_views = sync_piece_views(controller.board, piece_views, controller)
        for view in piece_views.values():
            view.update(dt_ms)
            view.update_pixel_pos(controller.engine)

        # אין יותר score_tracker.update / move_tracker.update —
        # ה-Bus מעדכן אותם אוטומטית כשקורים אירועים.

        snapshot = build_snapshot(
            controller.board, piece_views, controller.engine,
            score_tracker, move_tracker, selected=controller.selected,  banner=banner.current_text())
        canvas = renderer.render(snapshot)

        cv2.setMouseCallback(WINDOW_NAME, on_mouse, {
            "controller": controller,
        })
        cv2.imshow(WINDOW_NAME, canvas.img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_ui()