class Piece:
    def __init__(self, color, value):
        self.color = color
        self.value = value
        self.is_dama = False
        self.index = 0
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value})"

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
            first_element = element[0]
            if first_element is None:
                continue
            elif isinstance(first_element, Piece):
                color = first_element.color
                if color == 'r' and first_element.is_dama:
                    first_element.index = i
                    key, value = func2(first_element)
                    valid_moves.update({key: value})
    return valid_moves


def func2(piece):
    damamove = [7, 9, -9, -7]
    moves = []
    for mv in damamove:
        dest_index = piece.index
        holder = []
        while True:
            if dest_index < 0 or dest_index >= len(board_state) or board_state[dest_index] != []:
                break
            holder.append(dest_index)
            dest_index += mv
        moves.append(tuple(sorted(holder)))
    return (piece.index, moves)


# Test the code with your provided board state
board_state = [
    [None, '*'],
    'X', 
    [None, '/'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '+'], 
    'X', 
    'X', 
    [None, '/'], 
    'X', 
    [None, '*'], 
    'X', 
    [Piece('r', 2), '+'], 
    'X', 
    [Piece('r', 0), '-'], 
    [None, '-'], 
    'X', 
    [None, '+'], 
    'X', 
    [Piece('r', 6, is_dama=True), '*"], 
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
    [Piece('b', 0, is_dama=True), '*"], 
    'X', 
    [None, '/'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '+'], 
    'X', 
    'X', 
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
    'X', 
    'X', 
    [None, '+'], 
    'X', 
    [None, '-'], 
    'X', 
    [None, '/'], 
    'X', 
    [None, '*']
]

print(func1(board_state))
