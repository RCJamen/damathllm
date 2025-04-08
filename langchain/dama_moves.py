class Piece:
    def __init__(self, color, value, is_dama=False):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = 0
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, {self.is_dama})"

    def __eq__(self, other):
        return isinstance(other, Piece) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


def func1(board_state):
    valid_moves = {}
    for i, element in enumerate(board_state):
        if element == 'X':
            continue
        elif isinstance(element, list):
            first_element = element[0]
            if first_element is None:
                continue
            elif isinstance(first_element, Piece):
                if first_element.color == 'r' and first_element.is_dama:
                    first_element.index = i
                    key, value = func2(first_element)
                    valid_moves.update({key: value})
    return {**valid_moves}


def func2(piece):
    damamove = [7, 9, -9, -7]
    moves = []
    for mv in damamove:
        dest_index = piece.index
        holder = []
        while (dest_index + mv) >= 0 and (dest_index + mv) < len(board_state) and board_state[dest_index + mv][0] is None:
            holder.append(dest_index + mv)
            dest_index += mv
        if not holder:
            continue
        moves.append(tuple(holder))
    return piece.index, moves


# Example usage
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

# Test the functions
print(func1(board_state))
