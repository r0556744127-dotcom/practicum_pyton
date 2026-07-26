import sys
import os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "core"))

import json
import cv2
from websockets.sync.client import connect

from img import Img
from piece import Piece
from board_mapper import BoardMapper
from ui.ui_config import WINDOW_NAME, CELL_SIZE_PX
from ui.sprite_utils import sprite_path
from ui.ui_helpers import make_white_transparent
from ui.renderer import Renderer
from ui.game_snapshot import GameSnapshot, PieceSnapshot
from ui.room_dialog import ask_room_action, ask_lobby_choice, wait_for_guest_or_cancel
from ui.home_dialog import ask_home_action
from ui.motion_render import motion_pixel_pos
from ui.sound_player import SoundPlayer
from ui.banner import BannerEffect

SERVER_URL = "ws://127.0.0.1:8765"

_sprite_cache = {}


class _NetMotion:
    """Minimal motion object for motion_pixel_pos (same fields as core Motion)."""

    def __init__(self, data):
        self.from_row, self.from_col = data["from"]
        self.to_row, self.to_col = data["to"]
        self.arrival_time = data["arrival_time"]


def get_sprite(token):
    if token not in _sprite_cache:
        piece = Piece.parse(token)
        sprite = Img().read(sprite_path(piece, "idle", 0),
                            size=(CELL_SIZE_PX, CELL_SIZE_PX), keep_aspect=True)
        make_white_transparent(sprite)
        _sprite_cache[token] = sprite
    return _sprite_cache[token]


def build_pieces(board_rows, pending=None, clock=0):
    """Draw board pieces; in-flight pieces use smooth lerp (like local UI)."""
    pending = pending or []
    moving_from = {
        (p["from"][0], p["from"][1]): p for p in pending if p.get("token")
    }

    pieces = []
    for r, row in enumerate(board_rows):
        for c, token in enumerate(row):
            if token == ".":
                continue
            sprite = get_sprite(token)
            h, w = sprite.img.shape[:2]
            flight = moving_from.get((r, c))
            if flight is not None:
                x_px, y_px = motion_pixel_pos(_NetMotion(flight), clock, w, h)
            else:
                x_px = c * CELL_SIZE_PX + (CELL_SIZE_PX - w) // 2
                y_px = r * CELL_SIZE_PX + (CELL_SIZE_PX - h) // 2
            pieces.append(PieceSnapshot(
                sprite=sprite, x_px=x_px, y_px=y_px, row=r, col=c))
    return tuple(pieces)


def handle_click(x, y, state, selected, my_color, ws, mapper):
    row, col = mapper.to_cell(x, y)
    rows = state["board"]
    if not (0 <= row < len(rows) and 0 <= col < len(rows[0])):
        return selected

    token = rows[row][col]

    if token != "." and token[0] == my_color:
        return (row, col)

    if selected is not None:
        ws.send(json.dumps({
            "type": "move",
            "from": list(selected),
            "to": [row, col],
        }))
        return None

    return selected


def on_mouse(event, x, y, flags, clicks):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicks.append((x, y))


def login_or_register(ws):
    action, username, password = ask_home_action()
    if action is None:
        return None

    if action == "register":
        ws.send(json.dumps({
            "type": "register",
            "username": username,
            "password": password,
        }))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("type") == "register_result":
                if not msg.get("ok"):
                    print("register failed:", msg.get("message"))
                    return None
                break
            if msg.get("type") == "welcome":
                return msg
            if msg.get("type") == "error":
                print("error:", msg.get("message"))
                return None
        # server auto-logs in after successful register
        # but our server sends register_result then expects us to... 
        # actually server converts to login and sends welcome — wait for it

    if action == "login":
        ws.send(json.dumps({
            "type": "login",
            "username": username,
            "password": password,
        }))

    while True:
        welcome = json.loads(ws.recv())
        if welcome.get("type") == "error":
            print("login failed:", welcome.get("message"))
            return None
        if welcome.get("type") == "welcome":
            return welcome
        if welcome.get("type") == "register_result" and not welcome.get("ok"):
            print("register failed:", welcome.get("message"))
            return None


def run_client():
    ws = connect(SERVER_URL)
    welcome = login_or_register(ws)
    if welcome is None:
        ws.close()
        return

    print("logged in —",
          "user:", welcome.get("username"),
          "elo:", welcome.get("elo"))

    choice = ask_lobby_choice()
    if choice is None:
        ws.close()
        return

    room_code = None

    if choice == "room":
        action, code = ask_room_action()
        if action == "create":
            ws.send(json.dumps({"type": "create_room"}))
        elif action == "join":
            ws.send(json.dumps({"type": "join_room", "code": code}))
            room_code = code
        else:
            print("Room cancelled.")
            ws.close()
            return
    elif choice == "spectate":
        ws.send(json.dumps({"type": "spectate"}))
    else:
        ws.send(json.dumps({"type": "find_match"}))

    my_color = None
    wait_root = None
    cancel_flag = None

    while my_color is None:
        # Let Cancel work while waiting for a guest after Create
        if wait_root is not None:
            try:
                wait_root.update()
            except Exception:
                wait_root = None
            if cancel_flag and cancel_flag["value"]:
                ws.send(json.dumps({"type": "cancel_room"}))
                try:
                    wait_root.destroy()
                except Exception:
                    pass
                print("Room cancelled.")
                ws.close()
                return

        try:
            msg = json.loads(ws.recv(timeout=0.2))
        except TimeoutError:
            continue

        kind = msg.get("type")
        if kind == "searching":
            print(msg.get("message"))
        elif kind == "search_failed":
            print(msg.get("message"))
            ws.close()
            return
        elif kind == "room_created":
            room_code = msg.get("code")
            print(msg.get("message"))
            wait_root, cancel_flag = wait_for_guest_or_cancel(room_code)
        elif kind == "room_cancelled":
            print(msg.get("message"))
            ws.close()
            return
        elif kind == "error":
            print("error:", msg.get("message"))
            ws.close()
            return
        elif kind == "match_found":
            if wait_root is not None:
                try:
                    wait_root.destroy()
                except Exception:
                    pass
                wait_root = None
            my_color = msg["color"]
            if msg.get("code"):
                room_code = msg["code"]
            if my_color == "viewer":
                print("WATCHING:", msg.get("opponent"), "room:", room_code)
            else:
                print("MATCH! you are", my_color, "vs", msg.get("opponent"))

    mapper = BoardMapper(CELL_SIZE_PX)
    renderer = Renderer()
    sound = SoundPlayer()
    banner = BannerEffect()
    # Same start effects as local ui_app
    sound.on_game_started({})
    banner.on_game_started({})
    clicks = []
    selected = None
    state = None
    seen_activity = 0
    seen_bus = 0
    bus_synced = False  # skip old events already stored on server
    status_error = ""

    title = f"{WINDOW_NAME} - {my_color}"
    if room_code:
        title += f" [{room_code}]"
    cv2.namedWindow(title)
    cv2.setMouseCallback(title, on_mouse, clicks)

    while True:
        while True:
            try:
                data = json.loads(ws.recv(timeout=0))
            except TimeoutError:
                break
            if data["type"] == "state":
                state = data
                if state.get("room_code"):
                    room_code = state["room_code"]
            elif data["type"] == "move_result":
                status_error = f"move: {data['result']}"
                print("move_result:", data["result"])

        if state is not None:
            activity = state.get("activity") or []
            while seen_activity < len(activity):
                print("[activity]", activity[seen_activity])
                seen_activity += 1

            # Play sounds from EventBus events (same as ui_app)
            bus_events = state.get("bus_events") or []
            if not bus_synced:
                seen_bus = len(bus_events)
                bus_synced = True
            while seen_bus < len(bus_events):
                ev = bus_events[seen_bus]
                name = ev.get("event")
                data = ev.get("data") or {}
                if name == "move_made":
                    sound.on_move(data)
                elif name == "piece_captured":
                    sound.on_capture(data)
                elif name == "game_over":
                    sound.on_game_over(data)
                seen_bus += 1

            while clicks:
                x, y = clicks.pop(0)
                selected = handle_click(x, y, state, selected,
                                        my_color, ws, mapper)

            scores = state.get("scores") or {"w": 0, "b": 0}
            white_score = int(scores.get("w", 0))
            black_score = int(scores.get("b", 0))
            label = {"w": "WHITE", "b": "BLACK"}.get(my_color, "VIEWER")
            status = f"You: {label}"
            remaining = state.get("disconnect_remaining")
            if remaining is not None:
                status += f" | left: {remaining}s"
            if status_error:
                status += f" | {status_error}"

            move_lines = tuple(state.get("moves") or ())
            clock = state.get("clock", 0)
            pending = state.get("pending") or []

            snapshot = GameSnapshot(
                rows=len(state["board"]),
                cols=len(state["board"][0]),
                clock=clock,
                pieces=build_pieces(state["board"], pending, clock),
                score_text=status,
                moves_lines=move_lines,
                game_over=state["game_over"],
                selected=selected,
                banner=banner.current_text(),
                white_score=white_score,
                black_score=black_score,
            )
            canvas = renderer.render(snapshot)
            # Room ID on top of the board (teacher requirement)
            if room_code:
                cv2.putText(
                    canvas.img,
                    f"ROOM {room_code}",
                    (12, 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 220, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
            cv2.imshow(title, canvas.img)

        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            break

    ws.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_client()
