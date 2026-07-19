import time


class BannerEffect:
    """מנוי על ה-Bus: כרזה גדולה על הלוח לכמה שניות בתחילת המשחק.

    on_game_started נקרא ע"י ה-Bus ומדליק את הכרזה;
    current_text מחזיר את הטקסט להצגה — או None אם הזמן עבר.
    """

    def __init__(self, duration_sec: float = 2.5):
        self._duration = duration_sec
        self._text = None
        self._until = 0.0

    def on_game_started(self, data):
        self._text = "FIGHT!"
        self._until = time.time() + self._duration

    def current_text(self):
        if self._text is not None and time.time() < self._until:
            return self._text
        return None


if __name__ == "__main__":
    banner = BannerEffect(duration_sec=0.2)
    assert banner.current_text() is None      # עוד לא התחיל משחק
    banner.on_game_started({})
    assert banner.current_text() == "FIGHT!"  # הכרזה דולקת
    time.sleep(0.3)
    assert banner.current_text() is None      # הזמן עבר — הכרזה כבתה
    print("BannerEffect OK")