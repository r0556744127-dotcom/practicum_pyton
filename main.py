import sys
from MappBoard import MappBoard
from GameEngine import GameEngine
from TextTestRender import TextTestRender

class ChessBoardParser:
    """מנתח קלט פנימי המובנה ישירות במיין כדי למנוע יצירת קבצים מיותרים"""
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
                
            # זיהוי המקטעים השונים בקלט
            if line.startswith("לוח:"):
                current_section = "board"
                continue
            elif line.startswith("פקודות:"):
                current_section = "commands"
                continue
            
            # קריאת שורות הלוח
            if current_section == "board":
                tokens = line.split()
                if tokens:
                    self.board.add_row(tokens)
                    
            # קריאת שורות הפקודה
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
                
            action = parts[0]
            
            if action == "לחץ":
                x, y = int(parts[1]), int(parts[2])
                engine.handle_click(x, y)
                
            elif action == "המתן":
                ms = int(parts[1])
                engine.handle_wait(ms)
                
            elif action == "הדפס" and len(parts) > 1 and parts[1] == "לוח":
                snapshot = engine.create_snapshot()
                renderer.display(snapshot)
                
            elif action == "לוח" and len(parts) > 1 and parts[1] == "הדפס":
                snapshot = engine.create_snapshot()
                renderer.display(snapshot)

def main():
    # המערכת מפעילה את הפונקציה הזו ומעבירה את sys.stdin למחלקה שהגדרנו למעלה
    parser = ChessBoardParser(sys.stdin)
    board = parser.get_board()
    parser.execute_commands(board)

if __name__ == "__main__":
    main()