import subprocess
import json
import re
import ast
import random
import requests
from subprocess import check_output
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

FLASK_BASE_URL = "http://127.0.0.1:5000"

# --- Data Models and Helper Classes ---
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


# --- Request Models ---
class StartRequest(BaseModel):
    start: bool

class BoardRequest(BaseModel):
    board: str


# --- Utility Functions ---
def reinitialize_board(board_state, new_piece_class):
    new_board = []
    for cell in board_state:
        if isinstance(cell, list):
            if cell[0] is None:
                new_board.append([None, cell[1]])
            else:
                old_piece = cell[0]
                new_piece = new_piece_class(
                    color=old_piece.color,
                    value=old_piece.value,
                    is_dama=old_piece.is_dama,
                )
                new_board.append([new_piece, cell[1]])
        else:
            new_board.append(cell)
    return new_board

def get_valid_moves(test_name, board_state):
    try:
        if test_name == "normal_moves":
            from utilities.normal_moves import func1, Piece as NM_Piece
            import utilities.normal_moves
            new_board = reinitialize_board(board_state, NM_Piece)
            utilities.normal_moves.board_state = new_board
            result =  func1(new_board)
        elif test_name == "dama_moves":
            from utilities.dama_moves import func1, Piece as DM_Piece
            import utilities.dama_moves
            new_board = reinitialize_board(board_state, DM_Piece)
            utilities.dama_moves.board_state = new_board
            result =  func1(new_board)
        elif test_name == "normal_captures":
            from utilities.normal_captures import func5, Piece as NC_Piece
            import utilities.normal_captures
            new_board = reinitialize_board(board_state, NC_Piece)
            utilities.normal_captures.board_state = new_board
            result =  func5(new_board)
        elif test_name == "dama_captures":
            from utilities.dama_captures import func7, Piece as DC_Piece
            import utilities.dama_captures
            new_board = reinitialize_board(board_state, DC_Piece)
            utilities.dama_captures.board_state = new_board
            result =  func7(new_board)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def clean_dict(data):
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned_value = clean_dict(value)
            if cleaned_value:
                cleaned[key] = cleaned_value
        return cleaned
    elif isinstance(data, list):
        cleaned_list = [clean_dict(item) for item in data if item not in ([], ())]
        return [item for item in cleaned_list if item != {}]
    elif isinstance(data, tuple):
        cleaned_tuple = tuple(item for item in data if item not in ([], ()))
        return cleaned_tuple if cleaned_tuple else None
    return data

# --- Endpoints ---
@app.post("/generate_code")
def generate_code(request: StartRequest):
    if request.start:
        try:
            subprocess.run(['bash', 'utilities/script.sh'])
            return {"status": "completed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return {"status": "waiting"}

@app.post("/board_to_move")
def board_to_move(request: BoardRequest):
    try:
        board_state = eval(request.board)
    except Exception as e:
        return {"status": "error", "error": f"Invalid board format: {str(e)}"}

    results = {}

    print(board_state)

    for test in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
        results[test] = get_valid_moves(test, board_state)

    results = clean_dict(results)
    print("Cleaned:", results)

    if "dama_captures" in results.keys() or "normal_captures" in results.keys():
        is_capture = True
    else:
        is_capture = False

    move_template = ChatPromptTemplate.from_template("""
    You are given a dictionary named "results" that contains only two keys: "normal_moves" and "dama_moves".

    Each of these keys maps to a dictionary:
    - In "normal_moves", keys are integers, and values are lists of integers.
    - In "dama_moves", keys are integers, and values are lists of tuples of integers.

    Your task is:
    1. Ignore the top-level keys ("normal_moves" and "dama_moves") and work only with their inner dictionaries.
    2. Merge the two inner dictionaries into one:
        - For each shared key, keep the value from the "dama_moves".
        - Flatten all tuples in "dama_moves" values into one list of integers before merging.
        - If a key only exists in one of the dictionaries, use its value directly.
    3. The final result should be a JSON object with a single key "moves", whose value is the merged dictionary.
    4. All keys in the final dictionary should be strings.

    Here is the results dictionary:
    {results}

    Return only the final JSON with key "moves".
    """)

    capture_template = ChatPromptTemplate.from_template("""
    You are given a dictionary named "results" that may contain either one of these two keys: "normal_captures" and "dama_captures".

    Each of these keys maps to a dictionary:
    - In "normal_captures", keys are integers, and values are lists of integers.
    - In "dama_captures", keys are integers, and values are lists of tuples of integers.

    Your task is:
    1. Ignore the top-level keys and work only with the values of the inner dictionaries.
    2. Choose one of the inner dictionaries:
        - If "dama_captures" exists **and** is not empty, flatten the tuples in its values (i.e., convert each list of tuples into a list of integers), and use this dictionary.
        - Otherwise, use the "normal_captures" dictionary.
    3. The final result should be a JSON object with a single key "captures", whose value is the selected and possibly modified dictionary.
    4. All keys in the final dictionary should be strings.

    Here is the results dictionary:
    {results}

    Return only the final JSON with key "captures".
    """)

    # capture_template = ChatPromptTemplate.from_template("""
    # You are given a dictionary that contains either only two keys: "normal_captures" and "dama_captures".

    # Each of these keys maps to a dictionary:
    # - In "normal_captures", keys are integers, and values are lists of integers.
    # - In "dama_captures", keys are integers, and values are lists of tuples of integers.

    # Your task is:
    # 1. Ignore the top-level keys ("normal_captures" and "dama_captures") and work only with their inner dictionaries.
    # 2. Choose one of the two inner dictionaries:
    #     - If "dama_captures" has a value aside from an empty dictionary, flatten the tuples in the value, and keep this value as the remaining dictionary.
    #     - Else, keep the "normal_captures" value which is a dictionary.
    # 3. The final result should be a JSON object with a single key "captures", whose value is the remaining dictionary.
    # 4. All keys in the final dictionary should be strings.

    # Here is the dictionary:
    # {results}

    # Return only the final JSON with key "captures".
    # """)

    from pydantic import BaseModel, Field
    from typing import Dict, List

    class MovesSchema(BaseModel):
        moves: Dict[int, List[int]] = Field(
            ..., description="Mapping from key to list of values"
        )
    class CapturesSchema(BaseModel):
        captures: Dict[int, List[int]] = Field(
            ..., description="Mapping from key to list of values. These should come from either 'normal_captures' or 'dama_captures'"
        )

    temperature=0
    while True:
        try:
            print("Rerun with temp:", temperature, "is_capture:", is_capture, "results:", results)
            move_llm = ChatOllama(
                model="llama3.1:8b-instruct-fp16",
                temperature=temperature,
                format=MovesSchema.model_json_schema(),
            )

            capture_llm = ChatOllama(
                model="llama3.1:8b-instruct-fp16",
                temperature=temperature,
                format=CapturesSchema.model_json_schema(),
            )

            if is_capture:
                # determiner_chain = determiner_template | llm
                capture_chain = capture_template | capture_llm

                # response = determiner_chain.invoke({
                #     "results": results,
                # })
                # print("Determiner:", response.content.rstrip())
                response = capture_chain.invoke({
                    "results": results
                })
            else:
                move_chain: dict = move_template | move_llm

                response = move_chain.invoke({
                    "results": results,
                })

            filtered_results = response.content
            final_results = json.loads(filtered_results)
            # final_results = filtered_results
            valid_moves = final_results
            print("Final Valid Moves:")
            print(valid_moves)

            src_dest_pairs = []
            
            for key, value in valid_moves.items():
                value = {int(k): eval(v) if isinstance(v, str) else eval(str([eval(str(i)) for i in v])) for k, v in value.items()}

                print(key, value)
                if key == 'captures':
                    is_capture = True
                for source, destinations in value.items():
                    for destination in destinations:
                        if isinstance(destination, tuple) or isinstance(destination, list):
                            for item in destination:
                                src_dest_pairs.append([source,item])
                        else:
                            src_dest_pairs.append([source,destination])

            print("SRCDEST pairs:", src_dest_pairs)
            chosen_list = random.choice(src_dest_pairs)
            chosen_piece_src = chosen_list[0]
            chosen_piece_dest = chosen_list[1]

            if src_dest_pairs != [] and is_capture:
                for index, (source, dest) in enumerate(src_dest_pairs):
                    distance = dest - source
                    directions = [-7, -9, 7, 9]
                    for direction in directions:
                        if distance % direction == 0:
                            factor = distance // direction
                            if factor < 0:
                                direction = abs(direction)
                            print(f"Direction: {direction}, Multiplied by: {factor}")
                            break

                    enemy=False
                    middle = source
                    while middle != dest:
                        middle += direction
                        if isinstance(board_state[middle][0], Piece):

                            if board_state[middle][0].color == 'b':
                                enemy = True
                                break
                    if enemy:
                        try:
                            srcval = board_state[source][0].value
                            midval = board_state[middle][0].value
                            destop = board_state[dest][1]
                            print(f"{srcval}{destop}{midval}")
                            score = round(eval(f"{srcval}{destop}{midval}"))
                            capturing_is_dama = board_state[source][0].is_dama
                            captured_is_dama = board_state[middle][0].is_dama
                            if capturing_is_dama and captured_is_dama:
                                score *= 4
                            elif capturing_is_dama or captured_is_dama:
                                score *= 2
                        except ZeroDivisionError:
                            score = 0

                        src_dest_pairs[index] = (source, dest, score)
                print(src_dest_pairs)
            break
        except:
            print("Resultstovaliderror")
            temperature += 0.04
            if temperature > 1:
                temperature = 0
            else:
                continue


        # source, destination, score = chosen_list # di paman gud ni need ang score ron since i randomize sa nato.

        # so sako nasabtan, ang i return dari dapat kay ang move na mismo? di ko sure unsay json na format pero dapat src ug destination ra
    print("CHOICE:", chosen_piece_src, chosen_piece_dest)
    return {"source": chosen_piece_src, "destination": chosen_piece_dest}


# bag-ong endpoint for bestmove, 
# input: source dest 
# steps for best move:
    # create basemodel para iluwa https://python.langchain.com/docs/how_to/structured_output/#typeddict-or-json-schema
    # pasa src_dest_pairs and board_state
    # create new instructions (bahalag imo i putol2 same concept sa pag valid move)

    {(0,18): "Bati ni cya na move kay..",
     (16,34): "Nice ni na move kay positive sa imo, unya negative if kan on niya"}
@app.post("/board_to_move")
def best_move(request: BoardRequest):
    pass