import os
import json
from flask import request, jsonify, session
from typing import (Optional, Dict, List, Union, Any)
from agno.agent import Agent
from agno.models.ollama import Ollama
from . import damath

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

def board_to_valid_moves(board_str: str) -> str:
    """
    Use this function to return valid moves of red piece in a board list.

    Args:
        board_str (str): string list representation of the board.

    Returns:
        str: JSON string valid moves of the board by position key pairs.
    """
    transformed_data = (board_str
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
    )

    transformed_data = eval(transformed_data)

    board = transformed_data

    valid_moves = {"valid_moves": []}
    has_mandatory_capture = False
    mandatory_moves = []

    def check_capture(index, piece, visited=None):
        if visited is None:
            visited = []

        captures = []
        directions = []

        if piece['is_dama']:
            directions = [
                {"step": 7, "movement": 7},
                {"step": 9, "movement": 9},
                {"step": -7, "movement": -7},
                {"step": -9, "movement": -9}
            ]
        else:
            if piece['color'] == 'r':
                directions = [
                    {"step": 7, "movement": 14},
                    {"step": 9, "movement": 18}
                ]

        for direction in directions:
            current_idx = index
            step = direction["step"]

            while True:
                capture_idx = current_idx + step
                if not (0 <= capture_idx < 64):
                    break

                if (isinstance(board[capture_idx], list) and
                    board[capture_idx][0] is not None and
                    board[capture_idx][0]['color'] != piece['color'] and
                    capture_idx not in visited):

                    landing_idx = capture_idx + step
                    landing_spots = []

                    while 0 <= landing_idx < 64:
                        if not isinstance(board[landing_idx], list):
                            break
                        if board[landing_idx][0] is not None:
                            break
                        landing_spots.append(landing_idx)
                        if not piece['is_dama']:
                            break
                        landing_idx += step

                    for landing in landing_spots:
                        new_visited = visited + [index, capture_idx]
                        next_captures = check_capture(landing, piece, new_visited)

                        if next_captures:
                            for capture_path in next_captures:
                                captures.append([landing] + capture_path)
                        else:
                            captures.append([landing])

                if not piece['is_dama']:
                    break
                current_idx += step
                if not (0 <= current_idx < 64):
                    break

        return captures

    def get_dama_moves(index, piece):
        moves = [[], [], [], []]
        directions = [(7, 0), (9, 1), (-9, 2), (-7, 3)]
        for step, dir_idx in directions:
            current = index
            while True:
                next_pos = current + step
                if (0 <= next_pos < 64 and
                    isinstance(board[next_pos], list) and
                    board[next_pos][0] is None):
                    moves[dir_idx].append(next_pos)
                    current = next_pos
                else:
                    break
        return moves

    for index, cell in enumerate(board):
        if isinstance(cell, list) and isinstance(cell[0], dict):
            piece = cell[0]
            if piece['color'] == 'r':
                captures = check_capture(index, piece)
                if captures:
                    has_mandatory_capture = True
                    mandatory_moves.append({
                        "position": [index, cell[1]],
                        "piece": ["red", piece['value'], piece['is_dama']],
                        "destination": captures
                    })

    if has_mandatory_capture:
        valid_moves = {"valid_captures": mandatory_moves}
    else:
        valid_moves["valid_moves"] = []
        for index, cell in enumerate(board):
            if isinstance(cell, list) and isinstance(cell[0], dict):
                piece = cell[0]
                if piece['color'] == 'r':
                    if piece['is_dama']:
                        dama_moves = get_dama_moves(index, piece)
                        move = {
                            "position": [index, cell[1]],
                            "piece": ["red", piece['value'], piece['is_dama']],
                            "destination": dama_moves
                        }
                        valid_moves["valid_moves"].append(move)
                    else:
                        possible_moves = []
                        for delta in [7, 9]:
                            next_pos = index + delta
                            if (next_pos < 64 and isinstance(board[next_pos], list) and
                                board[next_pos][0] is None):
                                possible_moves.append(next_pos)
                        if possible_moves:
                            move = {
                                "position": [index, cell[1]],
                                "piece": ["red", piece['value'], piece['is_dama']],
                                "destination": possible_moves
                            }
                            valid_moves["valid_moves"].append(move)

    return json.dumps(valid_moves)

def get_valid_moves_logic(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = agno_get_valid_moves.run(message)
            if response.messages[-1].role != 'tool':
                return response.messages[-1].content
            print(f"Got tool response, attempt {attempt + 1} of {max_retries}")
            continue
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Error on attempt {attempt + 1} of {max_retries}: {str(e)}")
            continue

    raise ValueError(f"Failed to get valid response after {max_retries} attempts")


agno_get_valid_moves = Agent(
    model=Ollama(id="llama3-groq-tool-use:8b"),
    instructions=[
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
        "Never mix 'Move' and 'Capture' prefixes in the same response type."
    ],
    tools=[board_to_valid_moves],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True
)


@damath.route('/get_valid_moves', methods=['POST'])
def get_valid_moves():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400

        result = get_valid_moves_logic(data['message'])
        return jsonify({'response': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


agno_get_best_move = Agent(
    model=Ollama(id="llama3-groq-tool-use:8b"),
    # instructions=[
    #     # "Pass the arguments to board_to_valid_moves, wrap the board_str with double quotes.",
    #     "For each item in 'valid_moves', output '\"position\" - [destination]'.",
    #     "Example output:",
    #     "   Move from position [22, '/'] to [29, 31]",
    #     "   Move from position [18, '+'] to [[25], [27, 36, 45, 54, 63], [], [11, 4]]",
    #     "Keep 'position' and 'destination' structure intact.",
    # ],
    tools=[board_to_valid_moves],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True
)

@damath.route('/get_best_move', methods=['POST'])
def get_best_move():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request'}), 400

        print(data['message'])
        valid_moves = get_valid_moves_logic(data['message'])
        print(valid_moves)
        return jsonify({'board': data['message'], 'valid_moves':valid_moves}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500










# @damath.route('/clear_knowledge_base', methods=['POST'])
# def clear_knowledge_base():
#     global agent
#     if not agent or not agent.knowledge or not agent.knowledge.vector_db:
#         return jsonify({"error": "Agent not initialized or knowledge base not found"}), 400

#     agent.knowledge.vector_db.delete()

#     return jsonify({"status": "Knowledge base cleared"}), 200


# @damath.route('/agent_data', methods=['GET'])
# def get_run_ids():
#     if not agent:
#         return jsonify({"error": "Game agent not initialized or storage not found"}), 400

#     try:
#         run_ids = agent.storage.get_all_session_ids()
#         return jsonify({"run_ids": run_ids}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @damath.route('/print_chat_history', methods=['GET'])
# def print_chat_history():
#     global agent
#     if not agent:
#         return jsonify({"error": "Game Agent not initialized or memory not found"}), 400

#     chat_history = agent.get_chat_history()
#     print(chat_history)
#     return chat_history
