import sys

class ChessBoardParser:
    """אחראית על קריאת קלט גולמי ועיבודו לכדי אובייקט של לוח."""
    def __init__(self, input_stream=sys.stdin):
        self._stream = input_stream

    def parse(self):
        # שים לב: הסרנו את "-> ChessBoard" כדי למנוע את שגיאת ה-NameError
        from ChessBoard import ChessBoard  # ייבוא מקומי רק בזמן ריצת הפונקציה
        
        board = ChessBoard()
        has_started_reading = False

        for line in self._stream:
            tokens = line.strip().split()
            
            if not tokens:
                continue  # דילוג על שורות ריקות
                
            # נבצע את הבדיקה בעזרת מחלקת הלוח שקולטת את השורות
            # (הבדיקה הפנימית מול Piece תתבצע בתוך add_row)
            if has_started_reading and len(board._matrix) > 0:
                # אם כבר התחלנו לקרוא והגענו לשורה שאינה חלק מהלוח (למשל פלט שגוי)
                # נשתמש בטוקן הראשון כדי לבדוק באופן זמני אם הוא חוקי
                from Piece import Piece
                if not Piece.is_valid(tokens[0]):
                    break
            
            has_started_reading = True
            board.add_row(tokens)

        return board