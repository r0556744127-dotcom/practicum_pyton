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

SERVER_URL = "ws://127.0.0.1:8765"

_sprite_cache = {}


def get_sprite(token):
    if token not in _sprite_cache:
        piece = Piece.parse(token)
        sprite = Img().read(sprite_path(piece, "idle", 0),
                            size=(CELL_SIZE_PX, CELL_SIZE_PX), keep_aspect=True)
        make_white_transparent(sprite)
        _sprite_cache[token] = sprite
    return _sprite_cache[token]


def build_pieces(board_rows):
    pieces = []
    for r, row in enumerate(board_rows):
        for c, token in enumerate(row):
            if token == ".":
                continue
            sprite = get_sprite(token)
            h, w = sprite.img.shape[:2]
            pieces.append(PieceSnapshot(
                sprite=sprite,
                x_px=c * CELL_SIZE_PX + (CELL_SIZE_PX - w) // 2,
                y_px=r * CELL_SIZE_PX + (CELL_SIZE_PX - h) // 2,
                row=r, col=c))
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


def run_client():
    username = input("username: ").strip()
    password = input("password: ").strip()
    ws = connect(SERVER_URL)
    ws.send(json.dumps({
        "type": "login",
        "username": username,
        "password": password,
    }))

    # Wait until we get welcome/error (ignore any early state messages)
    while True:
        welcome = json.loads(ws.recv())
        if welcome.get("type") == "error":
            print("login failed:", welcome.get("message"))
            ws.close()
            return
        if welcome.get("type") == "welcome":
            break

    my_color = welcome["color"]
    print("connected as:", my_color,
          "user:", welcome.get("username"),
          "elo:", welcome.get("elo"))
    
    print("logged in — lobby. Asking server to find a match...")
    ws.send(json.dumps({"type": "find_match"}))

    my_color = None
    while my_color is None:
        msg = json.loads(ws.recv())
        if msg.get("type") == "searching":
            print(msg.get("message"))
        elif msg.get("type") == "search_failed":
            print(msg.get("message"))
            ws.close()
            return
        elif msg.get("type") == "match_found":
            my_color = msg["color"]
            print("MATCH! you are", my_color, "vs", msg.get("opponent"))
    mapper = BoardMapper(CELL_SIZE_PX)
    renderer = Renderer()
    clicks = []
    selected = None
    state = None

    title = f"{WINDOW_NAME} - {my_color}"
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
            elif data["type"] == "move_result":
                # Bug fix: show why a move did / did not happen
                print("move_result:", data["result"])

        if state is not None:
            while clicks:
                x, y = clicks.pop(0)
                selected = handle_click(x, y, state, selected,
                                        my_color, ws, mapper)

            label = {"w": "WHITE", "b": "BLACK"}.get(my_color, "VIEWER")
            score = f"You are: {label}"
            remaining = state.get("disconnect_remaining")
            if remaining is not None:
                score += f"  |  Opponent left: {remaining}s"
            snapshot = GameSnapshot(
                rows=len(state["board"]),
                cols=len(state["board"][0]),
                clock=0,
                pieces=build_pieces(state["board"]),
                score_text=score,
                game_over=state["game_over"],
                selected=selected,
            )
            canvas = renderer.render(snapshot)
            cv2.imshow(title, canvas.img)

        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            break

    ws.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_client()
