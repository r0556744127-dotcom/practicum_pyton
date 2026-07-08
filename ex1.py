# import sys

# def main():
#     VALID_PIECES = {
#         '.', 
#         'wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
#         'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'
#     }
    
#     lines = []
#     for line in sys.stdin:
#         lines.append(line.rstrip('\r\n'))
        
#     if not lines:
#         return

#     parsed_board = []
#     expected_width = None

#     for line in lines:
#         tokens = line.strip().split()
        
#         if not tokens:
#             continue
            
#         if tokens[0] not in VALID_PIECES:
#             if parsed_board:
#                 break
#             else:
#                 continue
                
#         current_width = len(tokens)
#         if expected_width is None:
#             expected_width = current_width
#         elif current_width != expected_width:
#             print("ERROR ROW_WIDTH_MISMATCH")
#             return

#         for token in tokens:
#             if token not in VALID_PIECES:
#                 print("ERROR UNKNOWN_TOKEN")
#                 return
                
#         parsed_board.append(tokens)

#     for row in parsed_board:
#         print(" ".join(row))

# if __name__ == '__main__':
#     main()