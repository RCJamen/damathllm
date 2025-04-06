class Piece:
    def __init__(self, color, value, is_dama=0, index=0, name=""):
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
        # Ignore 'X'
        if element == "X":
            continue

        # Check if the element is a list
        if isinstance(element, list):
            first_element = element[0]
            # Ignore None
            if first_element is None:
                continue

            # If it's an instance of Piece class
            if isinstance(first_element, Piece):
                piece = first_element
                # Check if the piece's color is 'r' and is a dama
                if piece.color == "r" and piece.is_dama:
                    # Assign index to the piece
                    piece.index = i
                    # Get valid moves from func2
                    key, value = func2(piece)
                    # Merge into valid_moves dictionary
                    valid_moves.update({key: value})
    return valid_moves


def func2(piece):
    damamove = [7, 9, -9, -7]
    moves = []

    for mv in damamove:
        dest_index = piece.index + mv
        holder = []

        while (0 <= dest_index < len(board_state) and
               board_state[dest_index][0] is None):
            holder.append(dest_index)
            dest_index += mv

        if holder:
            moves.append(tuple(holder))
    return piece.index, moves


# Example usage
board_state = [[None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X',
              [None, '/'], 'X', [None, '*'], 'X', [Piece('r', 2, is_dama=False), '+'], 'X',
              [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X',
              [Piece('r', 6, is_dama=True), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X',
              'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'],
              [Piece('b', 0, is_dama=True), '*'], 'X', [None, '/'], 'X', [None, '-'], 'X',
              [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X',
              [None, '-'], [Piece('r', -5, is_dama=True), '-'], 'X', [None, '+'], 'X',
              [None, '*'], 'X', [None, '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X',
              [None, '/'], [None, '*']]

print(func1(board_state))
