class Piece:
    def __init__(self, color, value, is_dama=False, index=0, name=''):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f'{color}, {value}'

    def __repr__(self):
        return f'Piece({self.color}, {self.value}, is_dama={self.is_dama})'

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def func1(board_state):
    valid_moves = {}
    for i, element in enumerate(board_state):
        if isinstance(element, str) and element == 'X':
            continue
        elif isinstance(element, list):
            piece = None
            if element[0] is not None:
                piece = Piece(element[0].color, element[0].value, element[0].is_dama)
                piece.index = i
            if piece is not None and piece.color == 'r':
                key, value = func2(piece)
                valid_moves.update({key: value})
    return valid_moves


def func2(piece):
    moves = []
    for destination_index in [piece.index + 7, piece.index + 9]:
        if destination_index >= len(board_state):
            continue
        destination_square = board_state[destination_index]
        if isinstance(destination_square, list) and destination_square[0] is None:
            moves.append(destination_index)
        elif isinstance(destination_square, (Piece, str)) or destination_square == 'X':
            continue
    return piece.index, moves


# Example usage with the provided board state
board_state = [[Piece('r', 2, is_dama=False), '*'], 'X', [Piece('r', -5, is_dama=False), '/'], 'X', 
              [Piece('r', 8, is_dama=False), '-'], 'X', [Piece('r', -11, is_dama=False), '+'], 'X', 'X', 
              [Piece('r', -7, is_dama=False), '/'], 'X', [Piece('r', 10, is_dama=False), '*'], 'X', 
              [Piece('r', -3, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [Piece('r', 4, is_dama=False), '-'], 'X', 
              [Piece('r', -1, is_dama=False), '+'], 'X', [Piece('r', 6, is_dama=False), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X', 'X', 
              [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], [None, '*'], 'X', [None, '/'], 'X', 
              [None, '-'], 'X', [None, '+'], 'X', 'X', [Piece('b', -9, is_dama=False), '/'], 'X', [Piece('b', 6, is_dama=False), '*'], 'X', 
              [Piece('b', -1, is_dama=False), '+'], 'X', [Piece('b', 4, is_dama=False), '-'], [Piece('b', 0, is_dama=False), '-'], 'X', 
              [Piece('b', -3, is_dama=False), '+'], 'X', [Piece('b', 10, is_dama=False), '*'], 'X', [Piece('b', -7, is_dama=False), '/'], 'X', 'X', 
              [Piece('b', -11, is_dama=False), '+'], 'X', [Piece('b', 8, is_dama=False), '-'], 'X', [Piece('b', -5, is_dama=False), '/'], 'X', 
              [Piece('b', 2, is_dama=False), '*']
             ]

print(func1(board_state))
