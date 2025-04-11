class Piece:
    def __init__(self, color, value, is_dama=0, index=0, name=""):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, {'dama' if self.is_dama else False})"

    def __eq__(self, other):
        return isinstance(other, Piece) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


# Board state
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
    'X', 
    'X',
    [None, '+'], 
    [Piece('b', -11, is_dama=False), '-'],
    'X', 
    [None, '/'], 
    'X', 
    [None, '*'], 
    [Piece('b', 0, is_dama=False), '*"], 
    'X', 
    [Piece('r', -5, is_dama=True), '/'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '+'], 
    'X', 
    'X', 
    [None, '/'], 
    'X', 
    [Piece('b', -5, is_dama=True), '*"], 
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
    'X', 
    'X',
    [None, '+'], 
    [None, '-'], 
    'X', 
    [None, '/'], 
    'X', 
    [Piece('r', 6, is_dama=False), '*']
]

def func7(board_state):
    valid_moves = {}
    for i, elem in enumerate(board_state):
        if isinstance(elem, str) and elem == 'X':
            continue
        elif isinstance(elem, list):
            first_elem = elem[0]
            if first_elem is None:
                continue
            elif isinstance(first_elem, Piece):
                if first_elem.color == 'r' and first_elem.is_dama:
                    piece_index = i
                    func8(first_elem, board_state)
                    valid_moves.update(func8(first_elem, board_state))
    return valid_moves


def func8(piece, board_state):
    capmoves = []
    dia = [7, 9, -7, -9]
    src_ind = piece.index
    for d in dia:
        capt_ind = src_ind + d
        while 0 <= capt_ind < len(board_state) and isinstance(board_state[capt_ind], list):
            if board_state[capt_ind][0] is None:
                capt_ind += d
                continue
            elif board_state[capt_ind][0].color == 'b':
                break
            else:
                capmoves.append((capt_ind, piece))
        if capt_ind >= len(board_state) or isinstance(board_state[capt_ind], list):
            break
    return {piece.index: capmoves for piece in capmoves}


# Example usage:
print(func7(board_state))
