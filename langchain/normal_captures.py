class Piece:
    def __init__(self, color, value, is_dama= False, index = 0, name=""):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{name}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, {self.is_dama})"

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)


def func5(board_state):
    valid_moves = {}
    for i, element in enumerate(board_state):
        if element == 'X':
            continue
        elif isinstance(element, list):
            first_element = element[0]
            if first_element is None:
                continue
            elif isinstance(first_element, Piece) and first_element.color == "r":
                first_element.index = i
            piece = func6(first_element)
            valid_moves.update(piece)
    return valid_moves


def func6(piece):
    capmoves = []
    dia = [7, 9, -7, -9]
    src_ind = piece.index

    for d in dia:
        temp_ind = src_ind + d
        if not 0 <= temp_ind < len(board_state):
            continue
        capt_ind = temp_ind
        if isinstance(board_state[capt_ind], list) and board_state[capt_ind][0] is not None \
                and isinstance(board_state[capt_ind][0], Piece) and board_state[capt_ind][0].color == "b":
            dest_ind = capt_ind + d
            if 0 <= dest_ind < len(board_state) and board_state[dest_ind] is not None:
                capmoves.append(dest_ind)
    return {piece.index: capmoves}


# Example usage:

board_state = [
    [Piece("r", -112, is_dama=False), '*'],
    'X', 
    [None, '/'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '+'], 
    'X', 
    'X', 
    [Piece("b", 0, is_dama=False), '/'], 
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
    [Piece("r", -9, is_dama=False), '/'], 
    'X', 
    'X', 
    [None, '+'], 
    'X', 
    [Piece("b", -11, is_dama=False), '-'], 
    'X', 
    [None, '/'], 
    'X', 
    [None, '*'], 
    [Piece("b", 0, is_dama=False), '*'], 
    'X', 
    [Piece("r", -5, is_dama=True), '/'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '+'], 
    'X', 
    'X', 
    [None, '/'], 
    'X', 
    [Piece("b", -5, is_dama=True), '*'], 
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
    [Piece("b", 6, is_dama=False), '/'], 
    'X', 
    'X', 
    [None, '+'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '/'], 
    'X', 
    [Piece("r", 6, is_dama=False), '*']
]

print(func5(board_state))
