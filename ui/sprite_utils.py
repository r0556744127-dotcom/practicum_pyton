import os
import json
from piece import Piece
from ui.ui_config import PIECES_ROOT

# כל המצבים האפשריים לפי המורה
ALL_STATES = ("idle", "move", "jump", "long_rest", "short_rest")
 


def piece_folder(piece: Piece) -> str:
    """
    ממיר כלי לשם תיקייה.
    דוגמאות:
      Piece('w', 'P') -> 'PW'
      Piece('b', 'K') -> 'KB'
    """
    return f"{piece.kind}{piece.color.upper()}"


def piece_states_root(piece: Piece) -> str:
    """נתיב לתיקיית states של כלי מסוים."""
    return os.path.join(PIECES_ROOT, piece_folder(piece), "states")


def state_folder(piece: Piece, state_name: str) -> str:
    """
    נתיב מלא לתיקיית state מסוים.
    דוגמה: pieces/PW/states/idle
    """
    return os.path.join(piece_states_root(piece), state_name)


def load_state_config(piece: Piece, state_name: str) -> dict:
    """
    קורא את config.json של state מסוים.
    מחזיר dict עם physics ו-graphics.
    """
    cfg_path = os.path.join(state_folder(piece, state_name), "config.json")
    if not os.path.isfile(cfg_path):
        raise FileNotFoundError(f"Missing config: {cfg_path}")

    with open(cfg_path, encoding="utf-8") as f:
        return json.load(f)


def get_physics_config(piece: Piece, state_name: str) -> dict:
    """
    מחזיר רק את החלק הפיזיקלי:
    speed_m_per_sec, next_state_when_finished
    """
    cfg = load_state_config(piece, state_name)
    return cfg["physics"]


def get_graphics_config(piece: Piece, state_name: str) -> dict:
    """
    מחזיר רק את החלק הגרפי:
    frames_per_sec, is_loop
    """
    cfg = load_state_config(piece, state_name)
    return cfg["graphics"]


def list_states(piece: Piece) -> list[str]:
    """
    מחזיר רשימת כל ה-states שקיימים בפועל לכלי.
    לדוגמה: ['idle', 'jump', 'long_rest', 'move', 'short_rest']
    """
    root = piece_states_root(piece)
    if not os.path.isdir(root):
        raise FileNotFoundError(f"Missing states folder: {root}")

    return sorted(
        name for name in os.listdir(root)
        if os.path.isdir(os.path.join(root, name))
    )


def list_sprites(piece: Piece, state_name: str) -> list[str]:
    """
    מחזיר רשימת קבצי PNG בתיקיית sprites של state.
    ממוינים לפי שם (1.png, 2.png, 3.png...)
    """
    sprites_dir = os.path.join(state_folder(piece, state_name), "sprites")
    if not os.path.isdir(sprites_dir):
        raise FileNotFoundError(f"Missing sprites folder: {sprites_dir}")

    return sorted(
        f for f in os.listdir(sprites_dir)
        if f.lower().endswith(".png")
    )


def sprite_path(piece: Piece, state_name: str, frame_index: int = 0) -> str:
    """
    מחזיר נתיב מלא לפריים מסוים.
    frame_index=0 -> הפריים הראשון.
    """
    sprites = list_sprites(piece, state_name)
    if not sprites:
        raise FileNotFoundError(
            f"No sprites in {state_folder(piece, state_name)}/sprites"
        )
    if frame_index < 0 or frame_index >= len(sprites):
        raise IndexError(
            f"frame_index {frame_index} out of range (0..{len(sprites)-1})"
        )
    return os.path.join(state_folder(piece, state_name), "sprites", sprites[frame_index])


def describe_state(piece: Piece, state_name: str) -> dict:
    """
    מחזיר סיכום נוח של state אחד.
    שימושי לבדיקה ולהדפסה.
    """
    physics = get_physics_config(piece, state_name)
    graphics = get_graphics_config(piece, state_name)
    sprites = list_sprites(piece, state_name)

    return {
        "piece": str(piece),
        "folder": piece_folder(piece),
        "state": state_name,
        "speed_m_per_sec": physics["speed_m_per_sec"],
        "next_state_when_finished": physics["next_state_when_finished"],
        "frames_per_sec": graphics["frames_per_sec"],
        "is_loop": graphics["is_loop"],
        "sprite_count": len(sprites),
        "first_sprite": sprites[0] if sprites else None,
    }


def describe_piece(piece: Piece) -> list[dict]:
    """מחזיר סיכום לכל ה-states של כלי אחד."""
    return [describe_state(piece, state) for state in list_states(piece)]