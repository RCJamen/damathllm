class Piece:
    def __init__(self, color, value, is_dama=False, index=0):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, is_dama={self.is_dama})"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


board_state = [
    [Piece('r', -112, is_dama=False), '*'],
    'X',
    [None, '/'],
    'X',
    [None, '-'],
    'X',
    [None, '+'],
    'X', 'X',
    [Piece('b', 0, is_dama=False), '/'],
    'X',
    [None, '*'],
    'X',
    [None, '+'],
    'X',
    [None, '-'],
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    [None, '*'],
    'X',
    [Piece('r', -9, is_dama=False), '/'],
    'X', 'X',
    [None, '+'],
    'X',
    [Piece('b', -11, is_dama=False), '-'],
    'X',
    [None, '/'],
    'X',
    [None, '*'],
    [Piece('b', 0, is_dama=False), '*'],
    'X',
    [Piece('r', -5, is_dama=True), '/'],
    'X',
    [None, '-'],
    'X',
    [None, '+'],
    'X', 'X',
    [None, '/'],
    'X',
    [Piece('b', -5, is_dama=True), '*'],
    'X',
    [None, '+'],
    'X',
    [None, '-'],
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    [None, '*'],
    'X',
    [Piece('b', 6, is_dama=False), '/'],
    'X', 'X',
    [None, '+'],
    'X',
    [None, '-'],
    'X',
    [None, '/'],
    'X',
    [Piece('r', 6, is_dama=False), '*']
]


def func5(board_state):
    valid_moves = {}
    for i, elem in enumerate(board_state):
        if isinstance(elem, str) and elem == 'X':
            continue
        elif isinstance(elem, list):
            first_elem = elem[0]
            if first_elem is None:
                continue
            if isinstance(first_elem, Piece) and first_elem.color == 'r':
                piece = first_elem
                piece.index = i
                key, value = func6(piece)
                valid_moves.update({key: value})
    return valid_moves


def func6(piece):
    capmoves = []
    dia = [7, 9, -7, -9]
    src_ind = piece.index

    for d in dia:
        temp_ind = src_ind + d
        if not 0 <= temp_ind < len(board_state):
            continue
        if isinstance(board_state[temp_ind], list) and board_state[temp_ind][0] is not None:
            first_piece = board_state[temp_ind][0]
            if first_piece.color == 'b':
                dest_ind = temp_ind + d
                if 0 <= dest_ind < len(board_state):
                    nested_list = board_state[dest_ind]
                    if isinstance(nested_list, list) and nested_list[0] is None:
                        capmoves.append(dest_ind)
    return piece.index, capmoves


def func7(valid_moves):
    # This function should update the valid moves dictionary
    pass  # For now, it's left empty as there are no instructions for what to do with this variable


# Call func5 and print the result
print(func5(board_state))
