"""Shared server constants (no logic)."""

FIND_TIMEOUT_SEC = 60
DISCONNECT_RESIGN_SEC = 20
TICK_MS = 50

# Same capture values as ui/ui_config.CAPTURE_POINTS
CAPTURE_POINTS = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}

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
