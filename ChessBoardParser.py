import sys

class ChessBoardParser:
     """אחראית על קריאת קלט גולמי ועיבודו לכדי אובייקט של לוח."""
    def __init__(self, input_stream=sys.stdin):
        self._stream = input_stream

    def parse(self):
        from ChessBoard import ChessBoard  
        
        board = ChessBoard()
        has_started_reading = False

        for line in self._stream:
            tokens = line.strip().split()
            
            if not tokens:
                continue 
                
           
            if has_started_reading and len(board._matrix) > 0:
               
                from Piece import Piece
                if not Piece.is_valid(tokens[0]):
                    break
            
            has_started_reading = True
            board.add_row(tokens)

        return board