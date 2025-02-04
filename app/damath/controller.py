import os
import json
import ast
import re
from flask import request, jsonify, session
from typing import (Optional, Dict, List, Union, Any)
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.models.ollama import Ollama
from agno.models.ollama import OllamaTools
# from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
# from agno.embedder.ollama import OllamaEmbedder
# from agno.vectordb.pgvector import PgVector2
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
    print("\n", board_str)
    print(type(board_str))

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

    print("\n", transformed_data)
    print(type(transformed_data))

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

        if not piece['is_dama']:
            if piece['color'] == 'r':
                directions = [(7, 14), (9, 18)]
        else:
            directions = [(7, 14), (9, 18), (-7, -14), (-9, -18)]

        for step, jump in directions:
            capture_idx = index + step
            landing_idx = index + jump

            if (0 <= capture_idx < 64 and 0 <= landing_idx < 64 and
                isinstance(board[capture_idx], list) and
                isinstance(board[landing_idx], list)):

                captured_piece = board[capture_idx][0]
                landing_spot = board[landing_idx][0]

                if (captured_piece is not None and
                    captured_piece['color'] != piece['color'] and
                    landing_spot is None and
                    capture_idx not in visited):

                    new_visited = visited + [index, capture_idx]
                    next_captures = check_capture(landing_idx, piece, new_visited)

                    if next_captures:
                        for capture_path in next_captures:
                            captures.append([landing_idx] + capture_path)
                    else:
                        captures.append([landing_idx])

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
        valid_moves["valid_moves"] = mandatory_moves
    else:
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



dammy = Agent(
    model=Ollama(id="llama3-groq-tool-use:8b"),
    instructions=[
        "For each item in 'valid_moves', output '\"position\" - [destination]'.",
        "Use the first element of 'position' and keep 'destination' structure intact.",
        "When passing arguments to board_to_valid_moves, wrap the board_str with double quotes."
    ],
    tools=[board_to_valid_moves],
    show_tool_calls=True,
    markdown=False,
    debug_mode=True
)

@damath.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    response = dammy.run(user_message)
    # print(response)
    return jsonify({"response": response.content}), 200

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
