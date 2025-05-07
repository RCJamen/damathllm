class Piece:
    def __init__(self, color, value, is_dama=0, index=0):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{color.capitalize()},{value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, {'dama' if self.is_dama else 'not dama'})"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


# Initialize the board state
board_state = [[None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', 
               [None, '/'], 'X', [None, '*'], 'X', [Piece('r', 2, is_dama=False), '+'], 'X', 
               [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X', 
               [Piece('r', 6, is_dama=True), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 
               'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], 
               [Piece('b', 0, is_dama=True), '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', 
               [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X', 
               [None, '-'], [Piece('r', -5, is_dama=True), '-'], 'X', [None, '+'], 'X', 
               [None, '*'], 'X', [None, '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', 
               [None, '/'], 'X', [None, '*']]

def func1(board_state):
    valid_moves = {}
    for i, element in enumerate(board_state):
        if isinstance(element, str) and element == 'X':
            continue
        elif isinstance(element, list):
            first_element = element[0]
            if first_element is None:
                continue
            if isinstance(piece, Piece) and piece.color == 'r' and piece.is_dama:
                piece.index = i
                key, value = func2(piece)
                valid_moves.update({key: value})
    return valid_moves


def func2(piece):
    damamove = [7, 9, -9, -7]
    moves = []
    for mv in damamove:
        dest_index = piece.index + mv
        holder = []
        while True:
            new_dest_index = dest_index + mv
            if (0 <= new_dest_index < len(board_state) and 
                board_state[new_dest_index][0] is None):
                holder.append(new_dest_index)
                dest_index = new_dest_index
            else:
                break
        moves.append(tuple(holder))
    return piece.index, moves


# Usage
result = func1(board_state)
print(result)
