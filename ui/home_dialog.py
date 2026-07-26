"""
Home screen window: Login or Register.
Returns one of:
  ("login", username, password)
  ("register", username, password)
  (None, None, None)  # closed / cancelled
"""
import tkinter as tk
from tkinter import messagebox


def ask_home_action():
    result = {"action": None, "username": None, "password": None}

    root = tk.Tk()
    root.title("Kung-Fu Chess — Home")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    tk.Label(root, text="Kung-Fu Chess", font=("Segoe UI", 16, "bold")).pack(
        padx=20, pady=(16, 4)
    )
    tk.Label(root, text="Login or create an account").pack(padx=20, pady=(0, 12))

    form = tk.Frame(root)
    form.pack(padx=20, pady=4)

    tk.Label(form, text="Username").grid(row=0, column=0, sticky="w", pady=4)
    user_var = tk.StringVar()
    user_entry = tk.Entry(form, textvariable=user_var, width=22, font=("Segoe UI", 11))
    user_entry.grid(row=0, column=1, pady=4, padx=(8, 0))
    user_entry.focus_set()

    tk.Label(form, text="Password").grid(row=1, column=0, sticky="w", pady=4)
    pass_var = tk.StringVar()
    tk.Entry(form, textvariable=pass_var, width=22, show="*", font=("Segoe UI", 11)).grid(
        row=1, column=1, pady=4, padx=(8, 0)
    )

    def read_fields():
        username = user_var.get().strip()
        password = pass_var.get()
        if not username or not password:
            messagebox.showwarning("Home", "Enter username and password.")
            return None
        return username, password

    def on_login():
        fields = read_fields()
        if not fields:
            return
        result["action"] = "login"
        result["username"], result["password"] = fields
        root.destroy()

    def on_register():
        fields = read_fields()
        if not fields:
            return
        result["action"] = "register"
        result["username"], result["password"] = fields
        root.destroy()

    def on_cancel():
        root.destroy()

    buttons = tk.Frame(root)
    buttons.pack(padx=20, pady=16)

    tk.Button(buttons, text="Login", width=12, command=on_login).pack(side="left", padx=4)
    tk.Button(buttons, text="Register", width=12, command=on_register).pack(side="left", padx=4)
    tk.Button(buttons, text="Cancel", width=12, command=on_cancel).pack(side="left", padx=4)

    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()

    return result["action"], result["username"], result["password"]


if __name__ == "__main__":
    print(ask_home_action())