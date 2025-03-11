from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import numpy as np
import json
from collections import defaultdict
from app.engine.base import BaseBoard, Color
from . import engine

board = None

@engine.route("/")
def index():
    return render_template("index.html")

@engine.route("/set_board/<string:board_type>")
def set_board(board_type):
    global board
    if board_type == "standard":
        from app.engine.damath import StandardBoard
        board = StandardBoard()
    return redirect(url_for("engine.index"))

@engine.route("/legal_moves")
def get_legal_moves():
    moves_dict = defaultdict(list)
    for move in list(board.legal_moves):
        moves_dict[int(move.square_list[0])].extend(map(int, move.square_list[1:]))
    return jsonify({"legal_moves": json.dumps(moves_dict)})

@engine.route("/fen")
def get_fen():
    return jsonify({"fen": board.fen})

@engine.route("/set_random_position")
def set_random_position():
    global board
    STARTING_POSITION = np.random.choice(
        [2, 0, -2, 1, -1], size=len(board.STARTING_POSITION), replace=True, p=[0.1, 0.6, 0.1, 0.1, 0.1]
    )
    board._moves_stack = []
    board._pos = STARTING_POSITION
    return get_position()

@engine.route("/position")
def get_position():
    history = []
    stack = board._moves_stack
    for idx in range(len(stack)):
        if idx % 2 == 0:
            history.append([(idx // 2) + 1, str(stack[idx])])
        else:
            history[-1].append(str(stack[idx]))
    return jsonify({
        "position": board.friendly_form.tolist(),
        "history": history,
        "turn": "blue" if board.turn == Color.WHITE else "red"
    })

@engine.route("/move/<string:source>/<string:target>", methods=["POST"])
def move(source, target):
    move_str = f"{source}-{target}"
    board.push_uci(move_str)
    return get_position()

@engine.route("/pop")
def pop():
    board.pop()
    return get_position()
