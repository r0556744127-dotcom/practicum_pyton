import sys

class PieceRules:
    """אחראית על חוקי התגים והתנועה התיאורטיים של הכלים."""
    VALID_TOKENS = {
        '.', 
        'wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
        'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'
    }

    @staticmethod
    def is_valid_token(token: str) -> bool:
        return token in PieceRules.VALID_TOKENS