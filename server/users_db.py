import os
import sqlite3
import hashlib
import secrets

# DB file next to this module
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")
STARTING_ELO = 1200


def _hash_password(password: str, salt: str) -> str:
    """Turn password + salt into a hex hash (never store the raw password)."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()


class UsersDB:
    """SQLite store for username / password / ELO."""

    def __init__(self, path: str = DB_PATH):
        self.path = path
        self._ensure_table()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _ensure_table(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    elo INTEGER NOT NULL
                )
            """)

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """Create a new user. Returns (ok, message)."""
        username = username.strip()
        if not username or not password:
            return False, "username and password required"
        if len(password) < 3:
            return False, "password too short (min 3)"

        salt = secrets.token_hex(16)
        password_hash = _hash_password(password, salt)

        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, salt, password_hash, elo) VALUES (?, ?, ?, ?)",
                    (username, salt, password_hash, STARTING_ELO),
                )
            return True, f"registered '{username}' with ELO {STARTING_ELO}"
        except sqlite3.IntegrityError:
            return False, "username already taken"

    def login(self, username: str, password: str) -> tuple[bool, str, int | None]:
        """Check credentials. Returns (ok, message, elo_or_None)."""
        username = username.strip()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT salt, password_hash, elo FROM users WHERE username = ?",
                (username,),
            ).fetchone()

        if row is None:
            return False, "unknown username", None

        salt, stored_hash, elo = row
        if _hash_password(password, salt) != stored_hash:
            return False, "wrong password", None

        return True, "login ok", elo

    def get_elo(self, username: str) -> int | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT elo FROM users WHERE username = ?",
                (username.strip(),),
            ).fetchone()
        return row[0] if row else None

    def set_elo(self, username: str, elo: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET elo = ? WHERE username = ?",
                (elo, username.strip()),
            )
    def apply_game_result(self, winner: str, loser: str) -> tuple[int, int]:
        """Update both players' ELO after a finished game."""
        from elo import update_pair
        
        w_elo = self.get_elo(winner)
        l_elo = self.get_elo(loser)
        if w_elo is None or l_elo is None:
            raise ValueError("winner or loser not found in DB")
        
        new_w, new_l = update_pair(w_elo, l_elo)
        self.set_elo(winner, new_w)
        self.set_elo(loser, new_l)
        return new_w, new_l        


if __name__ == "__main__":
    db = UsersDB()

    db.register("bob", "123")
    db.register("carol", "123")
    db.set_elo("bob", 1200)
    db.set_elo("carol", 1200)

    new_bob, new_carol = db.apply_game_result("bob", "carol")
    print("bob (winner):", new_bob)
    print("carol (loser):", new_carol)

    assert new_bob == 1216
    assert new_carol == 1184
    assert db.get_elo("bob") == 1216
    assert db.get_elo("carol") == 1184
    print("DB + ELO OK")
