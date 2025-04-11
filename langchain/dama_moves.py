class Piece:
    def __init__(self, color, value, is_dama=0, index=0, name=""):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = name

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, is_dama={self.is_dama})"

    def __eq__(self, other):
        if isinstance(other, Piece) and self.name == other.name:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.name)


def func1(board_state):
    valid_moves = {}
    for i, element in enumerate(board_state):
        if type(element) is str:
            continue
        elif isinstance(element, list):
            first_element = element[0]
            if first_element is None:
                continue
            piece = Piece(first_element.color, first_element.value, 
                          first_element.is_dama, i, f"{first_element.color}, {first_element.value}")
            if piece.color == 'r' and piece.is_dama:
                result = func2(piece)
                valid_moves.update(result)
    return valid_moves


def func2(piece):
    damamove = [7, 9, -9, -7]
    moves = []
    for mv in damamove:
        dest_index = piece.index + mv
        holder = []
        while 0 <= dest_index < len(board_state) and board_state[dest_index][0] is None:
            holder.append(dest_index)
            dest_index += mv
        if not holder:
            continue
        moves.append(tuple(holder))
    return {piece.index: moves}


# Example usage:
board_state = [[None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', 
              [Piece('r', -11, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X', 
              [Piece('r', 6, is_dama=True), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 
              'X', [None, '/'], 'X', [None, '*'], [Piece('b', 0, is_dama=True), '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', 
              [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X', [None, '-'], [Piece('r', -5, is_dama=True), 
              '-'], 'X', [None, '+'], 'X', [None, '*'], 'X', [None, '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 
              'X', [None, '*']]
print(func1(board_state))
