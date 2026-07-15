from board_mapper import BoardMapper

mapper = BoardMapper(cell_size=100)

print(mapper.to_pixel(0, 0))
print(mapper.to_pixel(7, 7))
print(mapper.to_pixel(0, 7))
print(mapper.to_pixel(7, 0))