import re
import json
import random

ROWS, COLS = 8, 8

operations = [
    ["*", 0, "/", 0, "-", 0, "+", 0],
    [0, "/", 0, "*", 0, "+", 0, "-"],
    ["-", 0, "+", 0, "*", 0, "/", 0],
    [0, "+", 0, "-", 0, "/", 0, "*"],
    ["*", 0, "/", 0, "-", 0, "+", 0],
    [0, "/", 0, "*", 0, "+", 0, "-"],
    ["-", 0, "+", 0, "*", 0, "/", 0],
    [0, "+", 0, "-", 0, "/", 0, "*"],
]

values = [
    ["2", 0, "-5", 0, "8", 0, "-11", 0],
    [0, "-7", 0, "10", 0, "-3", 0, "0"],
    ["4", 0, "-1", 0, "6", 0, "-9", 0],
    [0, "+", 0, "-", 0, "/", 0, "*"],
    ["*", 0, "/", 0, "-", 0, "+", 0],
    [0, "-9", 0, "6", 0, "-1", 0, "4"],
    ["0", 0, "-3", 0, "10", 0, "-7", 0],
    [0, "-11", 0, "8", 0, "-5", 0, "2"],
]

class Board:
    def __init__(self):
        self.board = []
        self.initialize_board()

    def initialize_board(self):
        temp_board = []
        for row in range(ROWS):
            temp_board.append([])
            for col in range(COLS):
                if col % 2 == (row % 2):
                    if row < 3:
                        temp_board[row].append(
                            (
                                Piece("r", int(values[row][col])),
                                row,
                                col,
                                operations[row][col],
                            )
                        )
                    elif row > 4:
                        temp_board[row].append(
                            (
                                Piece("b", int(values[row][col])),
                                row,
                                col,
                                operations[row][col],
                            )
                        )
                    else:
                        temp_board[row].append((None, row, col, operations[row][col]))
                else:
                    temp_board[row].append("X")

        self.board = []
        for row in temp_board:
            for item in row:
                if isinstance(item, tuple):
                    self.board.append([item[0], item[3]])
                else:
                    self.board.append("X")

    def to_json(self):
        json_board = []
        for position, item in enumerate(self.board):
            if isinstance(item, list):
                piece_data = {
                    "position": [position, item[1]],
                    "piece": None
                }
                if item[0] is not None:
                    piece = item[0]
                    color = 'red' if piece.color == 'r' else 'blue'
                    piece_data["piece"] = [color, piece.value, piece.is_dama]
                json_board.append(piece_data)
        return json.dumps({
            "board": json_board,
            "array_board": f"{self.board}"
        })

    def __repr__(self):
        return str(self.board)


class Piece:
    def __init__(self, color, value):
        self.value = value
        self.index = None
        self.color = color
        self.is_dama = False
        self.name = f"'{color}', {value}"
        self.capture_index = {}

    def __repr__(self):
        return f"Piece({self.name}, is_dama={self.is_dama})"

    def __eq__(self, other):
        return isinstance(other, Piece) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Game:
    def __init__(self):
        self.current_move = "b"
        self.board = Board()
        self.has_mandatory_capture = False
        self.has_mandatory_capture_check = False
        self.dama_mandatory_capture = False
        self.dama_mandatory_capture_check = False
        self.valid_moves = {}
        self.move_history = []
        self.scores = {"b": 0, "r": 0}
        self.over = False

    def check_all_valid(self, turn):
        self.valid_moves = {}
        for index, item in enumerate(self.board.board):
            if not isinstance(item, list):
                continue
            element = item[0]
            if not isinstance(element, Piece):
                continue
            if element.color != turn:
                continue
            element.capture_index = {}
            element.index = index
            self.valid_moves[element] = self.check_valid_moves(element)

    def check_potential_capture(self, piece):
        if piece.color == "r":
            left_movement = piece.index + 7
            right_movement = piece.index + 9
            bleft_movement = piece.index - 9
            bright_movement = piece.index - 7
            lls = left_movement + 7
            rls = right_movement + 9
            blls = bleft_movement - 9
            brls = bright_movement - 7
        elif piece.color == "b":
            left_movement = piece.index - 9
            right_movement = piece.index - 7
            bleft_movement = piece.index + 7
            bright_movement = piece.index + 9
            lls = left_movement - 9
            rls = right_movement - 7
            blls = bleft_movement + 7
            brls = bright_movement + 9

        diagonals = [left_movement, right_movement, bleft_movement, bright_movement]
        landing_squares = [lls, rls, blls, brls]
        for i, val in enumerate(diagonals):
            if val < 0 or val > 63:
                diagonals[i] = None
        for i, val in enumerate(landing_squares):
            if val < 0 or val > 63:
                landing_squares[i] = None

        capture_moves = []
        for i, val in enumerate(diagonals):
            if val is None:
                continue
            diagonal_square = self.board.board[val]
            if (
                isinstance(diagonal_square[0], Piece)
                and diagonal_square[0].color != self.current_move
            ):
                if landing_squares[i] is not None and self.board.board[landing_squares[i]][0] is None:
                    piece.capture_index[landing_squares[i]] = diagonals[i]
                    capture_moves.append(landing_squares[i])
                    self.has_mandatory_capture = True

        return capture_moves

    def check_dama_moves(self, piece):
        if piece.color == "r":
            dama_movement = {"left": 7, "right": 9, "bleft": -9, "bright": -7}
        elif piece.color == "b":
            dama_movement = {"left": -9, "right": -7, "bleft": 7, "bright": 9}

        dama_moves = []
        for direction in dama_movement.keys():
            starting_index = piece.index
            moves = []
            while True:
                starting_index += dama_movement[direction]
                if starting_index < 0 or starting_index > 63:
                    break
                if isinstance(self.board.board[starting_index][0], Piece):
                    if self.board.board[starting_index][0].color != self.current_move:
                        dama_capture_moves = self.dama_potential_capture(
                            piece, self.board.board[starting_index][0], direction
                        )
                        if dama_capture_moves:
                            piece.capture_index[dama_capture_moves] = starting_index
                            self.dama_mandatory_capture = True
                            if self.dama_mandatory_capture and not self.dama_mandatory_capture_check:
                                self.valid_moves = {}
                                dama_moves = []
                                self.dama_mandatory_capture_check = True
                            dama_moves.append(tuple(dama_capture_moves))
                        break
                    else:
                        break
                if not self.dama_mandatory_capture and not self.has_mandatory_capture:
                    if self.board.board[starting_index][0] is None:
                        moves.append(starting_index)
            if not self.dama_mandatory_capture:
                dama_moves.append(tuple(moves))
        return dama_moves

    def dama_potential_capture(self, piece, potential_capture_piece, direction):
        if piece.color == "r":
            dama_movement = {"left": 7, "right": 9, "bleft": -9, "bright": -7}
        elif piece.color == "b":
            dama_movement = {"left": -9, "right": -7, "bleft": 7, "bright": 9}

        capture_index = potential_capture_piece.index
        moves = []
        while True:
            capture_index += dama_movement[direction]
            if capture_index < 0 or capture_index > 63:
                break
            if isinstance(self.board.board[capture_index][0], Piece):
                break
            elif self.board.board[capture_index][0] is None:
                moves.append(capture_index)
        return tuple(moves)

    def check_valid_moves(self, piece):
        if piece.is_dama:
            moves = self.check_dama_moves(piece)
            return moves

        if self.dama_mandatory_capture:
            return []

        capture_moves = self.check_potential_capture(piece)

        if self.has_mandatory_capture:
            if not self.has_mandatory_capture_check:
                self.valid_moves = {}
                self.has_mandatory_capture_check = True
            if capture_moves:
                return capture_moves
            else:
                return []

        if piece.color == "r":
            left_movement = piece.index + 7
            right_movement = piece.index + 9
        elif piece.color == "b":
            left_movement = piece.index - 9
            right_movement = piece.index - 7

        valid_moves = []
        if 0 <= left_movement < 64:
            if self.board.board[left_movement][0] is None:
                valid_moves.append(left_movement)
        if 0 <= right_movement < 64:
            if self.board.board[right_movement][0] is None:
                valid_moves.append(right_movement)
        return valid_moves

    def valid_moves_to_json(self):
        valid_moves_json = {"valid_moves": []}
        for piece, moves in self.valid_moves.items():
            move = {
                "piece_index": piece.index,
                "piece": ["blue" if piece.color == "b" else "red", piece.value, piece.is_dama],
                "destinations": list(moves) if isinstance(moves, (list, tuple)) else moves
            }
            valid_moves_json["valid_moves"].append(move)
        return json.dumps(valid_moves_json)

    def api_move(self, piece_index, destination):
        self.has_mandatory_capture = False
        self.has_mandatory_capture_check = False
        self.dama_mandatory_capture = False
        self.dama_mandatory_capture_check = False
        self.check_all_valid(self.current_move)

        selected_piece = None
        selected_piece_moves = None
        for piece, moves in self.valid_moves.items():
            if piece.index == piece_index:
                selected_piece = piece
                selected_piece_moves = moves
                break

        if selected_piece is None:
            return {"error": "Invalid piece index or no valid moves for that piece."}

        valid = False
        if isinstance(selected_piece_moves, (list, tuple)):
            for move in (selected_piece_moves if isinstance(selected_piece_moves, list) else [selected_piece_moves]):
                if isinstance(move, tuple):
                    if destination in move:
                        valid = True
                        break
                else:
                    if destination == move:
                        valid = True
                        break
        if not valid:
            return {"error": "Invalid destination for the selected piece."}

        eaten = False
        score = 0

        if self.dama_mandatory_capture:
            for key in selected_piece.capture_index:
                if isinstance(key, tuple) and destination in key:
                    index_of_captured_piece = selected_piece.capture_index[key]
                    operator = self.board.board[destination][1]
                    if operator == '/':
                        operator = '//'
                    try:
                        raw_score = eval(f"{self.board.board[piece_index][0].value} {operator} {self.board.board[index_of_captured_piece][0].value}")
                        score = round(raw_score)
                        capturing_is_dama = self.board.board[piece_index][0].is_dama
                        captured_is_dama = self.board.board[index_of_captured_piece][0].is_dama
                        if capturing_is_dama and captured_is_dama:
                            score *= 4
                        elif capturing_is_dama or captured_is_dama:
                            score *= 2
                    except ZeroDivisionError:
                        score = 0
                    self.scores[self.current_move] += score
                    self.board.board[index_of_captured_piece][0] = None
                    eaten = True
                    break
        elif self.has_mandatory_capture:
            index_of_captured_piece = selected_piece.capture_index[destination]
            operator = self.board.board[destination][1]
            if operator == '/':
                operator = '//'
            try:
                raw_score = eval(f"{self.board.board[piece_index][0].value} {operator} {self.board.board[index_of_captured_piece][0].value}")
                score = round(raw_score)
                capturing_is_dama = self.board.board[piece_index][0].is_dama
                captured_is_dama = self.board.board[index_of_captured_piece][0].is_dama
                if capturing_is_dama and captured_is_dama:
                    score *= 4
                elif capturing_is_dama or captured_is_dama:
                    score *= 2
            except ZeroDivisionError:
                score = 0
            self.scores[self.current_move] += score
            self.board.board[index_of_captured_piece][0] = None
            eaten = True

        self.board.board[destination][0] = selected_piece
        selected_piece.index = destination
        self.board.board[piece_index][0] = None

        if (
            selected_piece.index in [0, 2, 4, 6] and selected_piece.color == "b"
            or selected_piece.index in [57, 59, 61, 63] and selected_piece.color == "r"
        ):
            selected_piece.is_dama = True

        self.move_history.append((self.current_move, (piece_index, destination), score))

        if eaten:
            chain_moves = self.check_valid_moves(selected_piece)
            print(chain_moves)
            if chain_moves:
                self.valid_moves = {selected_piece: chain_moves}
                return {
                    "array_board": f"{self.board}",
                    "scores": self.scores,
                    "current_turn": self.current_move,
                    "move_history": self.move_history,
                }
        self.current_move = "r" if self.current_move == "b" else "b"
        self.has_mandatory_capture = False
        self.has_mandatory_capture_check = False
        self.dama_mandatory_capture = False
        self.dama_mandatory_capture_check = False
        self.check_all_valid(self.current_move)

        return {
            "array_board": f"{self.board}",
            "current_turn": self.current_move,
            "scores": self.scores,
            "move_history": self.move_history,
        }
