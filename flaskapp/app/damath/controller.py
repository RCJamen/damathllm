import os
import json
import random
from flask import request, jsonify, session, render_template
from .damathengine import Game
from . import damath

game_instance = Game()

@damath.route('/')
def index():
    board_data = {
        "board": [
            # {"position": [0, "*"], "piece": ["red", 2, False]},
            # {"position": [2, "/"], "piece": ["red", -5, False]},
            # {"position": [4, "-"], "piece": ["red", 8, False]},
            # {"position": [6, "+"], "piece": ["red", -11, False]},
            # {"position": [9, "/"], "piece": ["red", -7, False]},
            # {"position": [11, "*"], "piece": ["red", 10, False]},
            # {"position": [13, "+"], "piece": ["red", -3, False]},
            # {"position": [15, "-"], "piece": ["red", 0, False]},
            # {"position": [16, "-"], "piece": ["red", 4, True]},
            # {"position": [18, "+"], "piece": ["red", -1, False]},
            # {"position": [20, "*"], "piece": ["red", 6, False]},
            # {"position": [22, "/"], "piece": ["red", -9, False]},
            # {"position": [25, "+"], "piece": None},
            # {"position": [27, "-"], "piece": None},
            # {"position": [29, "/"], "piece": None},
            # {"position": [31, "*"], "piece": None},
            # {"position": [32, "*"], "piece": None},
            # {"position": [34, "/"], "piece": None},
            # {"position": [36, "-"], "piece": None},
            # {"position": [38, "+"], "piece": None},
            # {"position": [41, "/"], "piece": ["blue", -9, False]},
            # {"position": [43, "*"], "piece": ["blue", 6, False]},
            # {"position": [45, "+"], "piece": ["blue", -1, False]},
            # {"position": [47, "-"], "piece": ["blue", 4, False]},
            # {"position": [48, "-"], "piece": ["blue", 0, False]},
            # {"position": [50, "+"], "piece": ["blue", -3, True]},
            # {"position": [52, "*"], "piece": ["blue", 10, False]},
            # {"position": [54, "/"], "piece": ["blue", -7, False]},
            # {"position": [57, "+"], "piece": ["blue", -11, False]},
            # {"position": [59, "-"], "piece": ["blue", 8, False]},
            # {"position": [61, "/"], "piece": ["blue", -5, False]},
            # {"position": [63, "*"], "piece": ["blue", 2, False]}
        ]
    }
    crown_icon = "static/img/crown-icon.svg"

    return render_template("index.html", board=board_data['board'], crown_icon=crown_icon)

@damath.route('/api/new_game', methods=['POST'])
def new_game():
    global game_instance
    game_instance = Game()
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
        "scores": game_instance.scores
    })
