from Render import Render
from GameSnapshot import GameSnapshot


class TextTestRender(Render):

    def display(self, snapshot: GameSnapshot) -> None:
        if snapshot.matrix:
            print("\n".join(" ".join(row) for row in snapshot.matrix))