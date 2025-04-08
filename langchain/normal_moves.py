class Piece:
    def __init__(self, color, value, is_dama=0, index=0):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, is_dama={self.is_dama})"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.name == other.name

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
            elif isinstance(first_element, Piece) and first_element.color == "r":
                piece = first_element
                piece.index = i
            else:
                continue
            key, value = func2(piece)
            valid_moves.update({key: value})
    return valid_moves


def func2(piece):
    moves = []
    for move in [7, 9]:
        dest_index = piece.index + move
        if dest_index < len(board_state):
            square = board_state[dest_index]
            if isinstance(square, list):
                first_element = square[0]
                if first_element is None:
                    moves.append(dest_index)
                elif isinstance(first_element, Piece) or first_element == 'X':
                    continue
                else:
                    moves.append(dest_index)
        else:
            continue
    return piece.index, moves


# Define the initial board state
board_state = [
    [Piece("r", 2, is_dama=False), '*'],
    'X', 
    [Piece("r", -5, is_dama=False), '/'], 
    'X', 
    [Piece("r", 8, is_dama=False), '-'], 
    'X', 
    [Piece("r", -11, is_dama=False), '+'], 
    'X', 
    'X', 
    [Piece("r", -7, is_dama=False), '/'], 
    'X', 
    [Piece("r", 10, is_dama=False), '*'], 
    'X', 
    [Piece("r", -3, is_dama=False), '+'], 
    'X', 
    [Piece("r", 0, is_dama=False), '-'], 
    [Piece("r", 4, is_dama=False), '-'], 
    'X', 
    [Piece("r", -1, is_dama=False), '+'], 
    'X', 
    [Piece("r", 6, is_dama=False), '*'], 
    'X', 
    [Piece("r", -9, is_dama=False), '/'], 
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
    [Piece("b", -9, is_dama=False), '/'], 
    'X', 
    [Piece("b", 6, is_dama=False), '*'], 
    'X', 
    [Piece("b", -1, is_dama=False), '+'], 
    'X', 
    [Piece("b", 4, is_dama=False), '-'], 
    [Piece("b", 0, is_dama=False), '-'], 
    'X', 
    [Piece("b", -3, is_dama=False), '+'], 
    'X', 
    [Piece("b", 10, is_dama=False), '*'], 
    'X', 
    [Piece("b", -7, is_dama=False), '/'], 
    'X', 
    'X', 
    [Piece("b", -11, is_dama=False), '+'], 
    'X', 
    [Piece("b", 8, is_dama=False), '-'], 
    'X', 
    [Piece("b", -5, is_dama=False), '/'], 
    'X', 
    [Piece("b", 2, is_dama=False), '*']
]

# Call func1 with the board state
print(func1(board_state))
