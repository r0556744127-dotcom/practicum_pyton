class BoardMapper:

    def __init__(self, cell_size):
        self.cell_size = cell_size

    def to_cell(self, x, y):
        row = y // self.cell_size
        col = x // self.cell_size
        return row, col
    
    def to_pixel(self, row, col):
        """Reverse of to_cell(): board grid cell -> top-left pixel
        coordinate of that cell on the board image. Used by the
        rendering layer to know where to draw a piece's sprite."""
        x = col * self.cell_size
        y = row * self.cell_size
        return x, y
