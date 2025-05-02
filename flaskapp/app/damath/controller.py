import os
import json
import random
import requests
from flask import request, jsonify, session, render_template, redirect, url_for
from .damathengine import Game
from . import damath
from .models import GameHistory

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
    try:
        url = FASTAPI_BASE_URL + "/generate_code"
        payload = {"start": True}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@damath.route('/api/board', methods=['GET'])
def get_board():
    return game_instance.board.to_json()

@damath.route('/api/set_board', methods=['POST'])
def set_board():
    data = request.get_json()
    game_instance.set_board(data.get('board'))
    return redirect(url_for('damath.get_board'))

@damath.route('/api/valid_moves', methods=['GET'])
def get_valid_moves():
    game_instance.check_all_valid(game_instance.current_move)
    return game_instance.valid_moves_to_json()

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

@damath.route('/api/proxy_ai_move', methods=['POST'])
def proxy_ai_move():
    try:
        data = request.json
        board = data.get('board')
        jsonboard = data.get('jsonboard')
        ai_response = requests.post(f'{FASTAPI_BASE_URL}/board_to_move',
            json={
                "board": board,
                "jsonboard": jsonboard
            })
        ai_response.raise_for_status()
        return jsonify(ai_response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to AI service: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    


# Database-related routes
@damath.route('/api/get_game_history', methods=['GET'])
def get_game_history():
    gamehist = GameHistory().all()
    print(gamehist, type(gamehist))
    return jsonify({
        "gamehistory": gamehist
    })


@damath.route('/api/add_game_history', methods=['POST'])
def add_game_history():
    data = request.json
    move_history = data.get('move_history')
    scores = data.get('scores')
    winner = data.get('winner')
    print(data)
    game_history = GameHistory(move_history=json.dumps({"move_history":move_history}),scores=scores,winner=winner)
    game_history.add()
    return {'message': 'Game history saved successfully'}, 200    