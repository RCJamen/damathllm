class Piece:
    def __init__(self, color, value, is_dama=0, index=0, name=''):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f'{color}, {value}'

    def __repr__(self):
        return f'Piece({self.color}, {self.value}, is_dama={self.is_dama})'

    def __eq__(self, other):
        if isinstance(other, Piece) and other.name == self.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)


def func1(board_state):
    valid_moves = {}
    for i, element in enumerate(board_state):
        if element == 'X':
            continue
        elif isinstance(element, list):
            piece = element[0]
            if piece is None:
                continue
            if not isinstance(piece, Piece) or piece.color != 'r':
                continue
            piece.index = i
            result = func2(piece)
            for key, value in result.items():
                valid_moves[key] = value
    return valid_moves


def func2(piece):
    moves = []
    for direction in [7, 9]:
        destination_index = piece.index + direction
        if 0 <= destination_index < len(board_state):
            square = board_state[destination_index]
            if isinstance(square, list) and square[0] is None:
                moves.append(destination_index)
            elif isinstance(square, Piece) or square == 'X':
                continue
    return {piece.index: moves}


board_state = [
    [Piece('r', 2, is_dama=False), '*'], 
    'X', 
    [Piece('r', -5, is_dama=False), '/'], 
    'X', 
    [Piece('r', 8, is_dama=False), '-'], 
    'X', 
    [Piece('r', -11, is_dama=False), '+'], 
    'X', 
    'X', 
    [Piece('r', -7, is_dama=False), '/'], 
    'X', 
    [Piece('r', 10, is_dama=False), '*'], 
    'X', 
    [Piece('r', -3, is_dama=False), '+'], 
    'X', 
    [Piece('r', 0, is_dama=False), '-'], 
    [Piece('r', 4, is_dama=False), '-'], 
    'X', 
    [Piece('r', -1, is_dama=False), '+'], 
    'X', 
    [Piece('r', 6, is_dama=False), '*'], 
    'X', 
    [Piece('r', -9, is_dama=False), '/'], 
    'X', 
    'X', 
    [None, '+'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '/'], 
    'X', 
    [None, '*'], 
    [None, '*'], 
    'X', 
    [None, '/'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '+'], 
    'X', 
    'X', 
    [Piece('b', -9, is_dama=False), '/'], 
    'X', 
    [Piece('b', 6, is_dama=False), '*'], 
    'X', 
    [Piece('b', -1, is_dama=False), '+'], 
    'X', 
    [Piece('b', 4, is_dama=False), '-'], 
    [Piece('b', 0, is_dama=False), '-'], 
    'X', 
    [Piece('b', -3, is_dama=False), '+'], 
    'X', 
    [Piece('b', 10, is_dama=False), '*'], 
    'X', 
    [Piece('b', -7, is_dama=False), '/'], 
    'X', 
    'X', 
    [Piece('b', -11, is_dama=False), '+'], 
    'X', 
    [Piece('b', 8, is_dama=False), '-'], 
    'X', 
    [Piece('b', -5, is_dama=False), '/'], 
    'X', 
    [Piece('b', 2, is_dama=False), '*']
]

print(func1(board_state))
