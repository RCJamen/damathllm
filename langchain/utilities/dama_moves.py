class Piece:
    def __init__(self, color, value, is_dama=0, index=0):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, {'dama' if self.is_dama else 'not dama'})"

    def __eq__(self, other):
        return isinstance(other, Piece) and self.name == other.name

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
                if first_element.color == 'r' and first_element.is_dama:
                    first_element.index = i
                    key, value = func2(first_element)
                    valid_moves.update({key: value})
                    valid_moves[i] = value  # Merge all pieces’ moves into the dictionary
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
        if holder:  # Only append the tuple to moves if it's not empty
            moves.append(tuple(holder))
    return piece.index, moves


# Board state as a list of lists
board_state = [[None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [Piece('r', -11, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X', [Piece('r', 6, is_dama=True), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], [Piece('b', 0, is_dama=True), "*"], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X', [None, '-'], [Piece('r', -5, is_dama=True), '-'], 'X', [None, '+'], 'X', [None, "*"], 'X', [None, '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, "*"]]

# Call func1 and print the result
print(func1(board_state))
