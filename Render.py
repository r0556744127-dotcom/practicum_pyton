class Render:
    
    def display(self, snapshot: 'GameSnapshot') -> None:
        raise NotImplementedError("יש לממש פונקציה זו במחלקות היורשות")

class TextTestRender(Render):
    """מציג טקסט קנוני עבור בדיקות ה-VPL."""
    
    def display(self, snapshot: 'GameSnapshot') -> None:
        # בודק קודם אם קיימת מטריצה ב-snapshot (תומך גם ב-matrix וגם ב-board_matrix)
        matrix = getattr(snapshot, 'matrix', None) or getattr(snapshot, 'board_matrix', None)
        
        if matrix:
            print("\n".join(" ".join(row) for row in matrix))