class Piece:
    def __init__(self, color, value, is_dama=0, index=0, name=""):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{name}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, {self.is_dama})"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def func7(board_state):
    valid_moves = {}
    for i, element in enumerate(board_state):
        if element == 'X':
            continue
        elif isinstance(element, list):
            piece = element[0]
            if not piece:
                continue
            if isinstance(piece, Piece) and piece.color == 'r' and piece.is_dama:
                piece.index = i
                key, value = func8(board_state, piece)
                valid_moves.update({key: value})
    return valid_moves


def func8(board_state, piece):
    capmoves = []
    dia = [7, 9, -7, -9]
    src_ind = piece.index

    for d in dia:
        capt_ind = src_ind + d
        holder = []

        while 0 <= capt_ind < len(board_state) and isinstance(board_state[capt_ind], list):
            if board_state[capt_ind][0] is None:
                capt_ind += d
                continue
            elif board_state[capt_ind][0].color == 'b':
                dest_ind = capt_ind + d
                while 0 <= dest_ind < len(board_state) and isinstance(board_state[dest_ind], list) and board_state[dest_ind][0] is None:
                    holder.append(dest_ind)
                    dest_ind += d
                break
            else:
                break

        capmoves.append(tuple(holder))
    return piece.index, capmoves


# Example usage
board_state = [
    [Piece('r', -112, is_dama=False), '*'],
    'X',
    [None, '/'],
    'X',
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    'X',
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
    'X',
    'X',
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
    'X',
    'X',
    [None, '+'],
    'X',
    [None, '-'],
    'X',
    [None, '/'],
    'X',
    [Piece('r', 6, is_dama=False), '*']
]

print(func7(board_state))
