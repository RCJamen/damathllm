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

def board_to_valid_moves(board: str) -> str:
    """
    Use this function to return valid moves of red piece in a board list.

    Args:
        board (str): list representation of the board.

    Returns:
        str: JSON string valid moves of the board by position key pairs.
    """
    print(board)
    print(type(board))
    def replace_piece(match):
        color, value, is_dama = match.groups()
        is_dama = is_dama == 'True'  # Convert string to boolean
        return f"{{'color': '{color}', 'value': {value}, 'is_dama': {is_dama}}}"

    board = re.sub(r'Piece\((r|b), (-?\d+), isdama=(True|False)\)', replace_piece, board)

    try:
        board = ast.literal_eval(board)
        print("Converted successfully to:", type(board))
    except Exception as e:
        print("Conversion error:", e)

    valid_moves = {"valid_moves": []}

    has_mandatory_capture = False
    mandatory_moves = []

    def check_capture(index, piece):
        captures = []
        if piece['color'] == 'r':
            if (index + 7 < 64 and isinstance(board[index + 7], list) and
                isinstance(board[index + 7][0], dict) and board[index + 7][0]['color'] == 'b'):
                if (index + 14 < 64 and isinstance(board[index + 14], list) and
                    board[index + 14][0] is None):
                    captures.append(index + 14)
            if (index + 9 < 64 and isinstance(board[index + 9], list) and
                isinstance(board[index + 9][0], dict) and board[index + 9][0]['color'] == 'b'):
                if (index + 18 < 64 and isinstance(board[index + 18], list) and
                    board[index + 18][0] is None):
                    captures.append(index + 18)
        return captures

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
    # instructions=[
    #     "When calling board_to_valid_moves tool, the board must match this exact structure:",
    #     "A list of 64 elements alternating between piece positions and 'X'",
    #     "Piece positions must be either:",
    #     "- [Piece(color, value, isdama=Boolean), operation]",
    #     "  where: color is 'r' or 'b'",
    #     "         value is an integer",
    #     "         operation is one of: '*', '/', '+', '-'",
    #     "- [None, operation]",
    #     "- 'X' for non-playable squares",
    #     "Example:",
    #     '''board_to_valid_moves("[[Piece(r, 2, isdama=False), '*'], 'X', [Piece(r, -5, isdama=False), '/'], 'X', ...]")''',
    #     "Maintain exact Piece() constructor format and operation symbols.",
    #     "All 64 positions must be included."
    # ],
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
    print(response)
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
