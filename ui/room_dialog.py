"""
Small Room window: Create / Join / Cancel.
Returns one of:
  ("create", None)
  ("join", "A3K9")
  ("cancel", None)
  (None, None)  # user closed the window
"""
import tkinter as tk
from tkinter import messagebox


def ask_room_action():
    result = {"action": None, "code": None}

    root = tk.Tk()
    root.title("Room")
    root.resizable(False, False)

    # Keep this window in front
    root.attributes("-topmost", True)

    tk.Label(root, text="Room", font=("Segoe UI", 14, "bold")).pack(padx=16, pady=(12, 4))
    tk.Label(root, text="Create a room, or join with a code:").pack(padx=16, pady=(0, 8))

    code_var = tk.StringVar()
    entry = tk.Entry(root, textvariable=code_var, width=16, font=("Consolas", 14))
    entry.pack(padx=16, pady=4)
    entry.focus_set()

    def on_create():
        result["action"] = "create"
        result["code"] = None
        root.destroy()

    def on_join():
        code = code_var.get().strip().upper()
        if not code:
            messagebox.showwarning("Room", "Type a room code first.")
            return
        result["action"] = "join"
        result["code"] = code
        root.destroy()

    def on_cancel():
        result["action"] = "cancel"
        result["code"] = None
        root.destroy()

    buttons = tk.Frame(root)
    buttons.pack(padx=16, pady=12)

    tk.Button(buttons, text="Create", width=10, command=on_create).pack(side="left", padx=4)
    tk.Button(buttons, text="Join", width=10, command=on_join).pack(side="left", padx=4)
    tk.Button(buttons, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=4)

    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()

    return result["action"], result["code"]


def wait_for_guest_or_cancel(code):
    """Show room code on screen; Cancel returns True if user cancels."""
    cancelled = {"value": False}
    root = tk.Tk()
    root.title("Waiting for guest")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    tk.Label(root, text="Room code (share with friend):",
             font=("Segoe UI", 11)).pack(padx=16, pady=(12, 4))
    tk.Label(root, text=code, font=("Consolas", 28, "bold"),
             fg="#0a7").pack(padx=16, pady=8)
    tk.Label(root, text="Waiting for someone to join...").pack(padx=16, pady=4)

    def on_cancel():
        cancelled["value"] = True
        root.destroy()

    tk.Button(root, text="Cancel", width=12, command=on_cancel).pack(pady=16)
    root.protocol("WM_DELETE_WINDOW", on_cancel)

    # Non-blocking: poll so the caller can also recv websocket
    root.update_idletasks()
    root.update()
    return root, cancelled


def ask_lobby_choice():
    """Home play menu. Returns 'find', 'room', 'spectate', or None."""
    result = {"choice": None}
    root = tk.Tk()
    root.title("Lobby")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    tk.Label(root, text="Lobby", font=("Segoe UI", 14, "bold")).pack(
        padx=16, pady=(12, 8))

    def pick(value):
        result["choice"] = value
        root.destroy()

    tk.Button(root, text="Play (find match)", width=22,
              command=lambda: pick("find")).pack(padx=16, pady=4)
    tk.Button(root, text="Room (Create / Join / Cancel)", width=22,
              command=lambda: pick("room")).pack(padx=16, pady=4)
    tk.Button(root, text="Spectate", width=22,
              command=lambda: pick("spectate")).pack(padx=16, pady=4)
    tk.Button(root, text="Quit", width=22,
              command=lambda: pick(None)).pack(padx=16, pady=(8, 16))

    root.protocol("WM_DELETE_WINDOW", lambda: pick(None))
    root.mainloop()
    return result["choice"]


if __name__ == "__main__":
    print(ask_room_action())