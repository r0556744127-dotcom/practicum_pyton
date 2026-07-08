import sys
from ChessBoardParser import ChessBoardParser
from ChessGame import ChessGame

def main():
    # 1. יצירת המפרש וקריאת הלוח מהקלט
    parser = ChessBoardParser(sys.stdin)
    board = parser.parse()
    
    # 2. אתחול מנוע המשחק עם הלוח שנקרא
    game = ChessGame(board)
    
    # איסוף כל השורות שנותרו לקריאה (כולל זו שהמפרש עצר בה)
    all_lines = parser.remaining_lines + [line.strip() for line in sys.stdin]
    
    # 3. לולאת עיבוד הפקודות
    for clean_line in all_lines:
        if not clean_line:
            continue
            
        # דילוג על כותרות אם נשארו כאלו בטעות
        if clean_line.lower().startswith(('לוח:', 'פקודות:', 'board:', 'commands:')):
            continue
            
        tokens = clean_line.split()
        if not tokens:
            continue
            
        command = tokens[0].lower()
        
        if command in ["click", "לחץ"]:
            if len(tokens) >= 3:
                x = int(tokens[1])
                y = int(tokens[2])
                game.handle_click(x, y)
                
        elif command in ["wait", "המתן"]:
            if len(tokens) >= 2:
                ms = int(tokens[1])
                game.handle_wait(ms)
                
        elif command in ["print", "הדפס", "לוח"]:
            game.handle_print()

if __name__ == '__main__':
    main()