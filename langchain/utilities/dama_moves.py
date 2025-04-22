class Piece:
    def __init__(self, color, value, is_dama=0, index=0, name=""):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, is_dama={self.is_dama})"

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


# Define the board state as a 1D array (list)
board_state = [
    [None, '*'],
    'X',
    [None, '/'],
    'X',
    [None, '-'],
    'X',
    [None, '+'],
    'X', 'X',
    [None, '/'],
    'X',
    [None, '*'],
    'X',
    [Piece('r', 2, is_dama=False), '+'],
    'X',
    [Piece('r', 0, is_dama=False), '-'],
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    [Piece('r', 6, is_dama=True), '*'],
    'X',
    [Piece('r', -9, is_dama=False), '/'],
    'X', 'X',
    [None, '+'],
    'X',
    [None, '-'],
    'X',
    [None, '/'],
    'X',
    [None, '*'],
    [Piece('b', 0, is_dama=True), '*'],
    'X',
    [None, '/'],
    'X',
    [None, '-'],
    'X',
    [None, '+'],
    'X', 'X',
    [None, '/'],
    'X',
    [None, '*'],
    'X',
    [None, '+'],
    'X',
    [None, '-'],
    [Piece('r', -5, is_dama=True), '-'],
    'X',
    [None, '+'],
    'X',
    [None, '*'],
    'X',
    [None, '/'],
    'X', 'X',
    [None, '+'],
    'X',
    [None, '-'],
    'X',
    [None, '/'],
    'X',
    [None, '*']
]


def func1(board_state):
    valid_moves = {}
    
    for i, element in enumerate(board_state):
        if isinstance(element, str) and element == 'X':
            continue
        elif isinstance(element, list):
            piece = element[0]
            if piece is None:
                continue
            if not isinstance(piece, Piece):
                continue
            if piece.color == 'r' and piece.is_dama:
                piece.index = i
                key, value = func2(piece)
                valid_moves.update({key: value})
    
    return {k: v for k, v in valid_moves.items()}


def func2(piece):
    damamove = [7, 9, -9, -7]
    moves = []
    for mv in damamove:
        dest_index = piece.index
        holder = []
        while True:
            new_dest_index = dest_index + mv
            if 0 <= new_dest_index < len(board_state) and board_state[new_dest_index][0] is None:
                holder.append(new_dest_index)
                dest_index = new_dest_index
            else:
                break
        moves.append(tuple(holder))
    return piece.index, moves


# Example usage
result = func1(board_state)
print(result)
