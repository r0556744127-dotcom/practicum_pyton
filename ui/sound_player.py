import winsound
import threading

# שמע של הפרויקט
def _play(notes):
    """מנגן רצף צלילים ב-thread רקע כדי לא לעצור את המשחק.

    notes = רשימה של (תדר בהרץ, משך במילישניות).
    """
    def run():
        for freq, dur in notes:
            winsound.Beep(freq, dur)
    threading.Thread(target=run, daemon=True).start()


class SoundPlayer:
    """מנוי על ה-Bus: צליל שונה לכל אירוע במשחק."""

    def on_game_started(self, data):
        _play([(523, 120), (659, 120), (784, 200)])   # מנגינה עולה

    def on_move(self, data):
        _play([(700, 70)])                            # ביפ קצר וגבוה

    def on_capture(self, data):
        _play([(300, 90), (250, 140)])                # "בום-בום" נמוך

    def on_game_over(self, data):
        _play([(600, 150), (450, 150), (300, 350)])   # מנגינה יורדת


if __name__ == "__main__":
    import time

    player = SoundPlayer()
    print("game started...")
    player.on_game_started({})
    time.sleep(1)
    print("move...")
    player.on_move({})
    time.sleep(1)
    print("capture...")
    player.on_capture({})
    time.sleep(1)
    print("game over...")
    player.on_game_over({})
    time.sleep(1.5)
    print("SoundPlayer OK")