from Render import Render
class TextTestRender(Render):
    """מציג טקסט קנוני עבור בדיקות ה-VPL."""
    def display(self, snapshot: GameSnapshot) -> None:
        if snapshot.matrix:
            print("\n".join(" ".join(row) for row in snapshot.matrix))