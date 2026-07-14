class BoardMapper:
#   אחראי על המיפוי בין הקואורדינטות הפיקסליות על המסך לבין משבצות הלוח.

    def __init__(self, cell_size):
        self.cell_size = cell_size

    def to_cell(self, x, y):
        row = y // self.cell_size
        col = x // self.cell_size
        return row, col
