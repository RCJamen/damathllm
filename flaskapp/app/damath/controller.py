import os
import json
import random
import requests
from flask import request, jsonify, session, render_template
from .damathengine import Game
from . import damath

game_instance = Game()

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

@damath.route('/')
def index():
    board_data = {"board": []}
    crown_icon = "static/img/crown-icon.svg"
    return render_template("index.html", board=board_data['board'], crown_icon=crown_icon)

@damath.route('/api/new_game', methods=['POST'])
def new_game():
    global game_instance
    game_instance = Game()

    url = FASTAPI_BASE_URL + "/generate_code"
    payload = {"start": True}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({"message": "New game started."})

@damath.route('/api/board', methods=['GET'])
def get_board():
    return game_instance.board.to_json()

@damath.route('/api/valid_moves', methods=['GET'])
def get_valid_moves():
    game_instance.check_all_valid(game_instance.current_move)
    return game_instance.valid_moves_to_json()

# http://127.0.0.1:5000/api/move
# add for red
@damath.route('/api/move', methods=['POST'])
def make_move():
    data = request.get_json()
    source = data.get('source')
    destination = data.get('destination')
    if source is None or destination is None:
        return jsonify({"error": "source and destination must be provided."}), 400
    result = game_instance.api_move(source, destination)
    return jsonify(result)

@damath.route('/api/move_history', methods=['GET'])
def move_history():
    return jsonify({
        "move_history": game_instance.move_history,
        "scores": game_instance.scores,
        "current_turn": game_instance.current_move,
    })
