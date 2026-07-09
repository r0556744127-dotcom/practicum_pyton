import sys
from MappBoard import MappBoard
from GameEngine import GameEngine
from TextTestRender import TextTestRender


class ChessBoardParser:
    """מנתח קלט של לוח שחמט ופקודות"""

    def __init__(self, stream):
        self.board = MappBoard()
        self.commands = []
        self._parse(stream)


    def _parse(self, stream):
        current_section = None

        for line in stream:
            line = line.strip()

            if not line:
                continue

            lower_line = line.lower()

            # זיהוי אזור הלוח
            if lower_line in ("board:", "לוח:"):
                current_section = "board"
                continue

            # זיהוי אזור הפקודות
            if lower_line in ("commands:", "פקודות:"):
                current_section = "commands"
                continue


            # קריאת הלוח
            if current_section == "board":
                tokens = line.split()

                if tokens:
                    self.board.add_row(tokens)


            # קריאת הפקודות
            elif current_section == "commands":
                self.commands.append(line)



    def get_board(self):
        return self.board



    def execute_commands(self, board):

        engine = GameEngine(board)
        renderer = TextTestRender()


        for cmd in self.commands:

            parts = cmd.split()

            if not parts:
                continue


            action = parts[0].lower()


            # לחיצה
            if action in ("click", "לחץ"):

                x = int(parts[1])
                y = int(parts[2])

                engine.handle_click(x, y)



            # המתנה
            elif action in ("wait", "המתן"):

                ms = int(parts[1])

                engine.handle_wait(ms)



            # הדפסת לוח
            elif action == "print":

                snapshot = engine.create_snapshot()

                renderer.display(snapshot)



            elif action == "board":

                if len(parts) > 1 and parts[1].lower() == "print":

                    snapshot = engine.create_snapshot()

                    renderer.display(snapshot)



def main():

    parser = ChessBoardParser(sys.stdin)

    board = parser.get_board()

    parser.execute_commands(board)



if __name__ == "__main__":
    main()