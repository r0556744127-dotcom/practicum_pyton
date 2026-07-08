from ChessBoardParser import ChessBoardParser
from ChessBoard import ChessBoard
def main():
    # מנהל זרימה (Controller) מינימליסטי - בדיוק כמו שמורים מעריכים
    parser = ChessBoardParser()
    board = parser.parse()
    
    if not board.is_empty():
        print(board.get_formatted_board())


if __name__ == '__main__':
    main()