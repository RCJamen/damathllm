import os
import json
import ast
from flask import request, jsonify, session
from typing import (Optional, Dict, List, Union, Any)
from agno.agent import Agent
from agno.models.ollama import Ollama
from . import damath

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# def board_to_valid_moves(board_str: str) -> str:
#     """
#     Use this function to return valid moves of red piece in a board list.

#     Args:
#         board_str (str): string list representation of the board.

#     Returns:
#         str: JSON string valid moves of the board by position key pairs.
#     """
#     transformed_data = (board_str
#         .replace('null', 'None')
#         .replace('true', 'True')
#         .replace('false', 'False')
#         .replace('Piece(r,', "{'color': 'r', 'value':")
#         .replace('Piece(b,', "{'color': 'b', 'value':")
#         .replace(', isdama=True)', ", 'is_dama': True}")
#         .replace(', isdama=False)', ", 'is_dama': False}")
#         .replace("+']", '+]')
#         .replace("'+]", '+]')
#         .replace("+]", "'+']")
#         .replace("-']", '-]')
#         .replace("'-]", '-]')
#         .replace("-]", "'-']")
#         .replace("*']", '*]')
#         .replace("'*]", '*]')
#         .replace("*]", "'*']")
#         .replace("/']", '/]')
#         .replace("'/]", '/]')
#         .replace("/]", "'/']")
#         .replace("]',", "],")
#     )

#     transformed_data = eval(transformed_data)

#     board = transformed_data

#     valid_moves = {"valid_moves": []}
#     has_mandatory_capture = False
#     mandatory_moves = []

#     def check_capture(index, piece, visited=None):
#         if visited is None:
#             visited = []

#         captures = []
#         directions = []

#         if piece['is_dama']:
#             directions = [
#                 {"step": 7, "movement": 7},   # down-left
#                 {"step": 9, "movement": 9},   # down-right
#                 {"step": -7, "movement": -7}, # up-right
#                 {"step": -9, "movement": -9}  # up-left
#             ]
#         else:
#             if piece['color'] == 'r':
#                 directions = [
#                     {"step": 7, "movement": 14},  # down-left
#                     {"step": 9, "movement": 18}   # down-right
#                 ]

#         for direction in directions:
#             current_idx = index
#             step = direction["step"]

#             while True:
#                 capture_idx = current_idx + step
#                 if not (0 <= capture_idx < 64):
#                     break

#                 if (isinstance(board[capture_idx], list) and
#                     board[capture_idx][0] is not None and
#                     board[capture_idx][0]['color'] != piece['color'] and
#                     capture_idx not in visited):

#                     landing_idx = capture_idx + step
#                     landing_spots = []

#                     while 0 <= landing_idx < 64:
#                         if not isinstance(board[landing_idx], list):
#                             break
#                         if board[landing_idx][0] is not None:
#                             break
#                         landing_spots.append(landing_idx)
#                         if not piece['is_dama']:
#                             break
#                         landing_idx += step

#                     for landing in landing_spots:
#                         new_visited = visited + [index, capture_idx]
#                         next_captures = check_capture(landing, piece, new_visited)

#                         if next_captures:
#                             for capture_path in next_captures:
#                                 captures.append([landing] + capture_path)
#                         else:
#                             captures.append([landing])

#                 if not piece['is_dama']:
#                     break
#                 current_idx += step
#                 if not (0 <= current_idx < 64):
#                     break

#         return captures

#     def get_dama_moves(index, piece):
#         moves = [[], [], [], []]
#         directions = [(7, 0), (9, 1), (-9, 2), (-7, 3)]
#         for step, dir_idx in directions:
#             current = index
#             while True:
#                 next_pos = current + step
#                 if (0 <= next_pos < 64 and
#                     isinstance(board[next_pos], list) and
#                     board[next_pos][0] is None):
#                     moves[dir_idx].append(next_pos)
#                     current = next_pos
#                 else:
#                     break
#         return moves

#     for index, cell in enumerate(board):
#         if isinstance(cell, list) and isinstance(cell[0], dict):
#             piece = cell[0]
#             if piece['color'] == 'r':
#                 captures = check_capture(index, piece)
#                 if captures:
#                     has_mandatory_capture = True
#                     mandatory_moves.append({
#                         "position": [index, cell[1]],
#                         "piece": ["red", piece['value'], piece['is_dama']],
#                         "destination": captures
#                     })

#     if has_mandatory_capture:
#         valid_moves = {"valid_captures": mandatory_moves}
#     else:
#         valid_moves["valid_moves"] = []
#         for index, cell in enumerate(board):
#             if isinstance(cell, list) and isinstance(cell[0], dict):
#                 piece = cell[0]
#                 if piece['color'] == 'r':
#                     if piece['is_dama']:
#                         dama_moves = get_dama_moves(index, piece)
#                         move = {
#                             "position": [index, cell[1]],
#                             "piece": ["red", piece['value'], piece['is_dama']],
#                             "destination": dama_moves
#                         }
#                         valid_moves["valid_moves"].append(move)
#                     else:
#                         possible_moves = []
#                         for delta in [7, 9]:
#                             next_pos = index + delta
#                             if (next_pos < 64 and isinstance(board[next_pos], list) and
#                                 board[next_pos][0] is None):
#                                 possible_moves.append(next_pos)
#                         if possible_moves:
#                             move = {
#                                 "position": [index, cell[1]],
#                                 "piece": ["red", piece['value'], piece['is_dama']],
#                                 "destination": possible_moves
#                             }
#                             valid_moves["valid_moves"].append(move)

#     return json.dumps(valid_moves)

def board_to_valid_moves(board: str) -> dict:
    """
    Use this function to return valid moves of red piece in a board list.

    Args:
        board (str): list dictionary representation of the board.

    Returns:
        str: JSON string valid moves of the board by position key pairs.
    """

    transformed_data = (board
        .replace('null', 'None')
        .replace('true', 'True')
        .replace('false', 'False')
        .replace("+']", '+]')
        .replace("'+]", '+]')
        .replace("+]", "'+']")
        .replace("-']", '-]')
        .replace("'-]", '-]')
        .replace("-]", "'-']")
        .replace("*']", '*]')
        .replace("'*]", '*]')
        .replace("*]", "'*']")
        .replace("/']", '/]')
        .replace("'/]", '/]')
        .replace("/]", "'/']")
        .replace("]',", "],")
        .replace("]}}]", "]}]")
    )

    print(transformed_data)

    # transformed_data = eval(transformed_data)
    # board = transformed_data

    board = ast.literal_eval(transformed_data)

    board_array = [None] * 64
    for piece_data in board:
        pos = piece_data['position'][0]
        if piece_data['piece'] is not None:
            board_array[pos] = piece_data

    valid_moves = []

    def is_valid_position(pos):
        return 0 <= pos < 64

    def get_piece_at(pos):
        return next((p for p in board if p['position'][0] == pos), None)

    def get_king_moves(pos):
        directions = [7, 9, -9, -7]
        king_moves = [[], [], [], []]

        for i, delta in enumerate(directions):
            current_pos = pos
            while True:
                next_pos = current_pos + delta
                if not is_valid_position(next_pos):
                    break
                next_piece = get_piece_at(next_pos)
                if next_piece and next_piece['piece'] is None:
                    king_moves[i].append(next_pos)
                    current_pos = next_pos
                else:
                    break
        return king_moves

    def get_capture_path(pos, delta, first_jump):
        """Returns all valid positions after a capture for kings"""
        path = [first_jump]
        current_pos = first_jump
        while True:
            next_pos = current_pos + delta
            if not is_valid_position(next_pos):
                break
            next_piece = get_piece_at(next_pos)
            if next_piece and next_piece['piece'] is None:
                path.append(next_pos)
                current_pos = next_pos
            else:
                break
        return path

    def check_for_captures():
        captures_exist = False
        for piece_data in board:
            if piece_data['piece'] is None or piece_data['piece'][0] != 'red':
                continue
            pos = piece_data['position'][0]
            directions = [7, 9, -9, -7]
            for delta in directions:
                next_pos = pos + delta
                jump_pos = next_pos + delta
                if is_valid_position(next_pos) and is_valid_position(jump_pos):
                    next_piece = get_piece_at(next_pos)
                    jump_piece = get_piece_at(jump_pos)
                    if (next_piece and next_piece['piece'] and
                        next_piece['piece'][0] == 'blue' and
                        jump_piece and jump_piece['piece'] is None):
                        captures_exist = True
                        break
            if captures_exist:
                break
        return captures_exist

    has_captures = check_for_captures()

    if has_captures:
        for piece_data in board:
            pos = piece_data['position'][0]
            if piece_data['piece'] is None or piece_data['piece'][0] != 'red':
                continue

            capture_moves = []
            if piece_data['piece'][2]:
                directions = [7, 9, -9, -7]
                for delta in directions:
                    next_pos = pos + delta
                    jump_pos = next_pos + delta
                    if is_valid_position(next_pos) and is_valid_position(jump_pos):
                        next_piece = get_piece_at(next_pos)
                        jump_piece = get_piece_at(jump_pos)
                        if (next_piece and next_piece['piece'] and
                            next_piece['piece'][0] == 'blue' and
                            jump_piece and jump_piece['piece'] is None):
                            capture_path = get_capture_path(pos, delta, jump_pos)
                            capture_moves.append(capture_path)
            else:  # Regular piece
                directions = [7, 9, -9, -7]
                for delta in directions:
                    next_pos = pos + delta
                    jump_pos = next_pos + delta
                    if is_valid_position(next_pos) and is_valid_position(jump_pos):
                        next_piece = get_piece_at(next_pos)
                        jump_piece = get_piece_at(jump_pos)
                        if (next_piece and next_piece['piece'] and
                            next_piece['piece'][0] == 'blue' and
                            jump_piece and jump_piece['piece'] is None):
                            capture_moves.append(jump_pos)

            if capture_moves:
                move = {
                    'position': piece_data['position'],
                    'piece': piece_data['piece'],
                    'destination': capture_moves
                }
                valid_moves.append(move)
    else:
        for piece_data in board:
            pos = piece_data['position'][0]
            if piece_data['piece'] is None or piece_data['piece'][0] != 'red':
                continue

            is_king = piece_data['piece'][2]
            if is_king:
                king_moves = get_king_moves(pos)
                if any(king_moves):
                    move = {
                        'position': piece_data['position'],
                        'piece': piece_data['piece'],
                        'destination': king_moves
                    }
                    valid_moves.append(move)
            else:
                possible_moves = []
                directions = [7, 9]
                for delta in directions:
                    next_pos = pos + delta
                    if is_valid_position(next_pos):
                        next_piece = get_piece_at(next_pos)
                        if next_piece and next_piece['piece'] is None:
                            possible_moves.append(next_pos)
                if possible_moves:
                    move = {
                        'position': piece_data['position'],
                        'piece': piece_data['piece'],
                        'destination': possible_moves
                    }
                    valid_moves.append(move)

    return json.dumps(valid_moves)

def get_valid_moves_logic(message, max_retries=10):
    for attempt in range(max_retries):
        try:
            response = valid_moves_agent.run(message)
            if len(response.messages) == 5 and response.messages[-2].tool_call_error == False:
                print(response, "\n\n")
                return response
            print(f"Got tool response, attempt {attempt + 1} of {max_retries}")
            continue
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Error on attempt {attempt + 1} of {max_retries}: {str(e)}")
            continue

    raise ValueError(f"Failed to get valid response after {max_retries} attempts")

def to_json(board_string):
    transformed_data = (board_string
        .replace('null', 'None')
        .replace('true', 'True')
        .replace('false', 'False')
        .replace('Piece(r,', "{'color': 'r', 'value':")
        .replace('Piece(b,', "{'color': 'b', 'value':")
        .replace(', isdama=True)', ", 'is_dama': True}")
        .replace(', isdama=False)', ", 'is_dama': False}")
        .replace("+']", '+]')
        .replace("'+]", '+]')
        .replace("+]", "'+']")
        .replace("-']", '-]')
        .replace("'-]", '-]')
        .replace("-]", "'-']")
        .replace("*']", '*]')
        .replace("'*]", '*]')
        .replace("*]", "'*']")
        .replace("/']", '/]')
        .replace("'/]", '/]')
        .replace("/]", "'/']")
        .replace("]',", "],")
    )

    board = eval(transformed_data)

    json_board = []
    for position, item in enumerate(board):
        if isinstance(item, list):
            piece_data = {
                "position": [position, item[1]],
                "piece": None
            }
            if item[0] is not None:
                piece = item[0]
                color = 'red' if piece['color'] == 'r' else 'blue'
                value = piece['value']
                piece_data["piece"] = [color, value, piece['is_dama']]
            json_board.append(piece_data)
    return json.dumps({"board": json_board})

valid_moves_agent = Agent(
    model=Ollama(id="llama3-groq-tool-use:8b"),
    instructions=[
        "Use the board data to generate valid moves using the tool 'board_to_valid_moves'",
        "Format output differently based on the type of moves:",
        "For 'valid_moves', always use:",
        "   Move from position [position:int] to [destination]",
        "For 'valid_captures', always use:",
        "   Capture from position [position:int] to [destination]",
        "Examples:",
        "For valid_moves:",
        "   Move from position [22, '/'] to [29, 31]",
        "   Move from position [18, '+'] to [[25], [27, 36, 45, 54, 63], [], [11, 4]]",
        "For valid_captures:",
        "   Capture from position [11, '*'] to [[29, 43]]",
        "   Capture from position [13, '+'] to [[27, 45], [27, 54]]",
        "Keep 'position' and 'destination' structure intact.",
        "Never mix 'Move' and 'Capture' prefixes in the same response type.",
    ],
    tools=[board_to_valid_moves],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)

best_move_agent = Agent(
    model=Ollama(id="llama3-groq-tool-use:8b"),
    instructions=[
        "You are an expert DaMath Checkers player. Analyze the board and make strategic moves.",
        "When deciding a move:",

        "1. Strategic Positioning:",
        "   - Advance pieces towards the center and opponent's side",
        "   - Control key squares that restrict opponent movement",
        "   - Create connected piece formations for mutual support",
        "   - Build towards king row advancement",

        "2. Operation Square Strategy:",
        "   - Master the board's operation layout (+, −, ×, ÷)",
        "   - Place positive-value pieces on subtraction (−) or division (÷) squares",
        "   - Place negative-value pieces on addition (+) or multiplication (×) squares",
        "   - Plan moves based on the operation of the landing square",

        "3. Defensive Considerations:",
        "   - Keep pieces protected by nearby friendly pieces",
        "   - Avoid leaving pieces isolated or vulnerable",
        "   - Maintain flexible movement options",
        "   - Maximize your position while limiting opponent's opportunities",

        "4. Forward Planning:",
        "   - Use the board's operation layout to guide future moves",
        "   - Position pieces to control multiple diagonal paths",
        "   - Create favorable setups for future turns",
        "   - Consider long-term strategic advantages",

        "Important: Provide your move with EXACTLY ONE destination position in this format:",
        "From [starting position] to [single destination position]",
        "Example: From [9] to [13]",

        "Reasoning (if any):",
        "1. [Immediate position benefit]",
        "2. [Operation square advantage]",
        "3. [Defensive consideration]",
        "4. [Future strategic opportunity]"
    ],
    markdown=True,
    debug_mode=True
)

    # instructions=[
    # "**Prioritize High-Score Captures:**",
    # "   - If the board has 'valid_captures', use the 'get_scores_from_captures' tool.,",
    # "   - Capture chips on addition (+) or multiplication (×) squares for higher scores.",
    # "   - Avoid capturing on subtraction (−) or division (÷) squares unless necessary.",
    # "   - Add 1 setence explanation to your output."
    # "5. Leverage Dama for High-Score Captures:",
    # "   - If a piece has `is_dama = True`, prioritize it for high-value captures.",
    # "   - Use its movement to reach better capture opportunities.",
    # "   - Position it strategically for future high-scoring moves while minimizing risks.",
    # ],
    # tools=[get_scores_from_captures],
    # show_tool_calls=True,


@damath.route('/get_valid_moves', methods=['POST'])
def get_valid_moves():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400
        result = get_valid_moves_logic(data['message'])
        return jsonify({'response': result.messages[-1].content}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@damath.route('/get_best_move', methods=['POST'])
def get_best_move():
    def get_moves(board_data):
            valid_moves = get_valid_moves_logic(board_data)
            last_message_content = json.loads(valid_moves.messages[-2].content)

            if 'valid_moves' in last_message_content:
                return last_message_content['valid_moves']
            elif 'valid_captures' in last_message_content:
                return last_message_content['valid_captures']
            return None

    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400

        json_board = to_json(data['message'])
        moves = get_moves(data['message'])

        board_and_move = {
            "board": json.loads(json_board)['board'],
            "valid_moves": moves
        }

        result = best_move_agent.run(str(board_and_move))

        return jsonify({'response': result.messages[-1].content}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
