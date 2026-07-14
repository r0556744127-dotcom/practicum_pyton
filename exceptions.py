# הגדרה של שגיאות מיוחדות שהמערכת יכולה לזרוק (כדי לדעת בדיוק מה השתבש).
class UnknownToken(ValueError):
    pass


class RowWidthMismatch(ValueError):
    pass
