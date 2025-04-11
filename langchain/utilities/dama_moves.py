class Piece:
    def __init__(self, color, value, is_dama=False, index=0):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, {self.is_dama})"

    def __eq__(self, other):
        return isinstance(other, Piece) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


board_state = [[None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [Piece('r', 2, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X', [Piece('r', 6, is_dama=True), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], [Piece('b', 0, is_dama=True), '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X', [None, '-'], [Piece('r', -5, is_dama=True), '-'], 'X', [None, '+'], 'X', [None, '*'], 'X', [None, '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*']]


def func2(piece):
    damamove = [7, 9, -9, -7]
    moves = []
    for mv in damamove:
        dest_index = piece.index
        holder = []
        while True:
            if 0 <= dest_index < len(board_state) and board_state[dest_index][0] is None:
                holder.append(dest_index)
                break
            else:
                dest_index += mv
                if dest_index >= len(board_state) or board_state[dest_index][0] is not None:
                    break
        moves.append(tuple(holder))
    return piece.index, moves


def func1(board):
    valid_moves = {}
    for i, element in enumerate(board):
        if isinstance(element, str) and element == 'X':
            continue
        elif isinstance(element, list):
            first_element = element[0]
            if first_element is None:
                continue
            elif isinstance(first_element, Piece):
                color = first_element.color
                if color == 'r' and first_element.is_dama:
                    piece = first_element
                    key, value = func2(piece)
                    valid_moves.update({key: value})
    return valid_moves


def main():
    board = [[None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [Piece('r', 2, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X', [Piece('r', 6, is_dama=True), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], [Piece('b', 0, is_dama=True), '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X', [None, '-'], [Piece('r', -5, is_dama=True), '-'], 'X', [None, '+'], 'X', [None, '*'], 'X', [None, '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*']]
    print(func1(board))


if __name__ == "__main__":
    main()
