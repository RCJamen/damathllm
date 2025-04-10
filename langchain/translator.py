import re

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


def translate(board_str):
    # Remove any extra quotes
    board_str = board_str.strip('"\'')

    # Pattern to match Piece objects in the string
    pattern = r'Piece\(([rb]), (-?\d+), isdama=(True|False)\)'

    def replace_piece(match):
        color, value, is_dama = match.groups()
        piece_dict = {
            "color": color,
            "value": int(value),
            "is_dama": is_dama.lower() == 'true'
        }
        return str(piece_dict)

    # Replace Piece objects with dictionaries
    board_str = re.sub(pattern, replace_piece, board_str)
    # Evaluate the string to create the actual board structure
    board = eval(board_str)
    return board

def visualize_board(board_state):
    # Initialize empty board
    board = []
    operations = []

    # Process each board position
    for item in board_state:
        if item == 'X':
            board.append('X')
            operations.append('')
        elif isinstance(item, list):
            if item[0] is None:
                board.append('___')
            else:
                piece = item[0]
                value = piece['value'] if isinstance(piece, dict) else piece.value
                color = piece['color'] if isinstance(piece, dict) else piece.color
                is_dama = 't' if (isinstance(piece, dict) and piece['is_dama']) else 'f'
                board.append(f"{value}{color}{is_dama}")
            operations.append(item[1])

    # Print board row by row
    print("\n  Checkers Board Visualization:")
    print("  " + "-" * 65)

    for row in range(8):
        row_items = []
        for col in range(8):
            index = row * 8 + col
            cell = board[index]
            op = operations[index]
            row_items.append(f"{op}.{index:2d}.{cell:6}")
        print(f"{row + 1}|", " ".join(row_items), "|")

    print("  " + "-" * 65)
    print("  Format: operation.position.value+color+isdama")
    print("  r=red, b=black, f=regular piece, t=dama/king")


def new_visualize_board(board_state):
    # Initialize empty board
    board = []
    operations = []

    # Process each board position
    for item in board_state:
        if item == 'X':
            board.append('X')
            operations.append('')
        elif isinstance(item, list):
            if item[0] is None:
                board.append('_')
            else:
                piece = item[0]
                value = piece['value'] if isinstance(piece, dict) else piece.value
                color = piece['color'] if isinstance(piece, dict) else piece.color
                is_dama = 't' if (isinstance(piece, dict) and piece['is_dama']) else 'f'
                board.append(f"{color}")
            operations.append(item[1])

    # Print board row by row
    print("\n  Checkers Board Visualization:")
    print("  " + "-" * 65)

    for row in range(8):
        row_items = []
        for col in range(8):
            index = row * 8 + col
            cell = board[index]
            op = operations[index]
            if cell == '_':
                row_items.append(f"{index:2d}")
            elif cell == 'X':
                row_items.append(f"X")
            elif cell == 'r' or cell == 'b':
                row_items.append(f"{index:2d}{cell}")
        print(f"{row + 1}|", "    ".join(row_items), "|")

    print("  " + "-" * 65)
    print("  Format: operation.position.value+color+isdama")
    print("  r=red, b=black, f=regular piece, t=dama/king")


# Test the code
if __name__ == "__main__":
    # Your board data
    board_data = """[[Piece(r, 2, isdama=False), '*'], 'X', [Piece(r, -5, isdama=False), '/'], 'X', [Piece(r, 8, isdama=False), '-'], 'X', [Piece(r, -11, isdama=False), '+'], 'X', 'X', [Piece(r, -7, isdama=False), '/'], 'X', [Piece(r, 10, isdama=False), '*'], 'X', [Piece(r, -3, isdama=False), '+'], 'X', [Piece(r, 0, isdama=False), '-'], [Piece(r, 4, isdama=False), '-'], 'X', [Piece(r, -1, isdama=False), '+'], 'X', [Piece(r, 6, isdama=False), '*'], 'X', [Piece(r, -9, isdama=False), '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], [None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [Piece(b, -9, isdama=False), '/'], 'X', [Piece(b, 6, isdama=False), '*'], 'X', [Piece(b, -1, isdama=False), '+'], 'X', [Piece(b, 4, isdama=False), '-'], [Piece(b, 0, isdama=False), '-'], 'X', [Piece(b, -3, isdama=False), '+'], 'X', [Piece(b, 10, isdama=False), '*'], 'X', [Piece(b, -7, isdama=False), '/'], 'X', 'X', [Piece(b, -11, isdama=False), '+'], 'X', [Piece(b, 8, isdama=False), '-'], 'X', [Piece(b, -5, isdama=False), '/'], 'X', [Piece(b, 2, isdama=False), '*']]"""

    # Translate and visualize
    translated = translate(board_data)

    visualize_board(translated)

    new_visualize_board(translated)
