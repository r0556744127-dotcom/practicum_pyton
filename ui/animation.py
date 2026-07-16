import os

from img import Img
from piece import Piece
from ui.ui_config import CELL_SIZE_PX
from ui.sprite_utils import (
    get_graphics_config,
    get_physics_config,
    list_sprites,
    state_folder,
)


class Animation:
    """טוען את כל פריימי state אחד (idle, move, ...) + config."""

    def __init__(self, piece: Piece, state_name: str, cell_size: int = CELL_SIZE_PX):
        self.piece = piece
        self.state_name = state_name

        graphics = get_graphics_config(piece, state_name)
        physics = get_physics_config(piece, state_name)

        self.fps = graphics["frames_per_sec"]
        self.is_loop = graphics["is_loop"]
        self.speed_m_per_sec = physics["speed_m_per_sec"]
        self.next_state = physics["next_state_when_finished"]

        self.frames = self._load_frames(cell_size)
        self.index = 0
        self.elapsed_ms = 0
        self.finished = False

    def _load_frames(self, cell_size: int) -> list[Img]:
        """טוען את כל קבצי ה-PNG מתיקיית sprites."""
        from ui.ui_helpers import make_white_transparent   # ← כאן
        sprite_names = list_sprites(self.piece, self.state_name)
        folder = state_folder(self.piece, self.state_name)
        sprites_dir = os.path.join(folder, "sprites")

        frames = []
        for name in sprite_names:
            path = os.path.join(sprites_dir, name)
            img = Img().read(path, size=(cell_size, cell_size), keep_aspect=True)
            make_white_transparent(img)
            frames.append(img)

        return frames

    def current(self) -> Img:
        """מחזיר את הפריים הנוכחי."""
        if not self.frames:
            raise FileNotFoundError(
                f"No frames for {self.piece} state {self.state_name}"
            )
        return self.frames[self.index]

    def frame_count(self) -> int:
        return len(self.frames)

    def update(self, dt_ms: int) -> None:
        """מקדם את האנימציה לפי הזמן שעבר."""
        if not self.frames or self.finished:
            return

        self.elapsed_ms += dt_ms
        frame_ms = 1000 / max(self.fps, 1)

        while self.elapsed_ms >= frame_ms:
            self.elapsed_ms -= frame_ms
            self.index += 1

            if self.index >= len(self.frames):
                if self.is_loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.finished = True
                    break