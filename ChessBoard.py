import sys

class ChessBoardParser:
    """אחראית על קריאת קלט גולמי ועיבודו לכדי אובייקט של לוח."""
    
    def __init__(self, input_stream=sys.stdin):
        self._stream = input_stream

    def parse(self):
        from ChessBoard import ChessBoard  
        
        board = ChessBoard()
        
        # שמירת השורות שנקראו כדי שנוכל להחזיר אותן לשימוש ב-main במידת הצורך
        self.remaining_lines = []

        for line in self._stream:
            clean_line = line.strip()
            if not clean_line:
                continue
                
            # אם נתקלנו בכותרת של הלוח או הפקודות - פשוט מדלגים עליה
            if clean_line.lower().startswith(('לוח:', 'פקודות:', 'board:', 'commands:')):
                continue

            tokens = clean_line.split()
            
            # אם המילה הראשונה היא פקודה מוכרת, סימן שסיימנו לקרוא את הלוח
            if tokens[0].lower() in ['click', 'wait', 'print', 'לחץ', 'המתן', 'הדפס', 'לוח']:
                self.remaining_lines.append(clean_line)
                break
                
            # אחרת, זו שורת לוח רגילה
            board.add_row(tokens)

        return board