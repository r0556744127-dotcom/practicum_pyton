import sys
class ChessBoard:
    """
    אחריות: ניהול מבנה הנתונים של הלוח ואכיפת חוקי המבנה שלו (ורידציה).
    המחלקה הזו לא יודעת מאיפה מגיע הקלט (מקלדת, קובץ או רשת) - היא רק מנהלת את הלוח.
    """
    def __init__(self):
        self._matrix = []
        self._expected_width = None

    def add_row(self, tokens: list[str]) -> None:
        """מוסיפה שורה ללוח ומבצעת בדיקות תקינות מיידיות."""
        # 1. בדיקת תקינות תתי-הטוקנים (הכלים)
        for token in tokens:
            if not Piece.is_valid(token):
                print("ERROR UNKNOWN_TOKEN")
                sys.exit(0)

        # 2. בדיקת אחידות רוחב השורות
        current_width = len(tokens)
        if self._expected_width is None:
            self._expected_width = current_width
        elif current_width != self._expected_width:
            print("ERROR ROW_WIDTH_MISMATCH")
            sys.exit(0)

        self._matrix.append(tokens)

    def is_empty(self) -> bool:
        return len(self._matrix) == 0

    def get_formatted_board(self) -> str:
        """מחזירה ייצוג טקסטואלי של הלוח (הפרדת לוגיקה מהדפסה)."""
        return "\n".join(" ".join(row) for row in self._matrix)