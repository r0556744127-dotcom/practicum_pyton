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

SERVER_URL = "ws://localhost:8765"

# מטמון ספרייטים: טוענים כל תמונת כלי פעם אחת בלבד
_sprite_cache = {}


def get_sprite(token):
    """מחזיר ספרייט לאסימון כמו 'bR' — מהמטמון, או טוען מהדיסק."""
    if token not in _sprite_cache:
        piece = Piece.parse(token)
        sprite = Img().read(sprite_path(piece, "idle", 0),
                            size=(CELL_SIZE_PX, CELL_SIZE_PX), keep_aspect=True)
        make_white_transparent(sprite)
        _sprite_cache[token] = sprite
    return _sprite_cache[token]


def build_pieces(board_rows):
    """הופך את רשימת האסימונים מהשרת ל-PieceSnapshots לציור."""
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
    """לחיצה ראשונה בוחרת כלי שלי; שנייה שולחת בקשת מהלך לשרת."""
    row, col = mapper.to_cell(x, y)
    rows = state["board"]
    if not (0 <= row < len(rows) and 0 <= col < len(rows[0])):
        return selected

    token = rows[row][col]

    # לחיצה על כלי בצבע שלי — בחירה (או החלפת בחירה)
    if token != "." and token[0] == my_color:
        return (row, col)

    # יש כבר כלי נבחר — שולחים בקשת מהלך; השרת יחליט אם חוקי
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
    ws = connect(SERVER_URL)
    welcome = json.loads(ws.recv())          # ההודעה הראשונה: welcome
    my_color = welcome["color"]
    print("connected as:", my_color)

    mapper = BoardMapper(CELL_SIZE_PX)
    renderer = Renderer()
    clicks = []
    selected = None
    state = None

    title = f"{WINDOW_NAME} - {my_color}"
    cv2.namedWindow(title)
    cv2.setMouseCallback(title, on_mouse, clicks)

    while True:
        # שואבים את כל העדכונים שהצטברו ושומרים את האחרון
        while True:
            try:
                data = json.loads(ws.recv(timeout=0))
            except TimeoutError:
                break
            if data["type"] == "state":
                state = data

        if state is not None:
            while clicks:
                x, y = clicks.pop(0)
                selected = handle_click(x, y, state, selected,
                                        my_color, ws, mapper)

            label = {"w": "WHITE", "b": "BLACK"}.get(my_color, "VIEWER")
            snapshot = GameSnapshot(
                rows=len(state["board"]),
                cols=len(state["board"][0]),
                clock=0,
                pieces=build_pieces(state["board"]),
                score_text=f"You are: {label}",
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