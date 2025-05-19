import subprocess
import json
import re
import ast
import random
import requests
import csv
import os
from subprocess import check_output
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

last_board_state = None
switch = False
temperature = 0
valid_choice = False
valid_choice_pairs = []
app = FastAPI()

results_to_move_chain = 'results_to_move.csv'
results_to_capture_chain = 'results_to_capture.csv'

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
    jsonboard: str


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
    global last_board_state, switch, temperature, valid_choice, valid_choice_pairs
    try:
        board_state = eval(request.board)
    except Exception as e:
        return {"status": "error", "error": f"Invalid board format: {str(e)}"}

    results = {}

    print(board_state)
    # if last_board_state == board_state:
    #     switch = not switch

    # FOR BEST MOVE
    print("This is JSON Board State:", request.jsonboard)
    print("\n",not valid_choice,not (last_board_state == board_state),not valid_choice or not (last_board_state == board_state))
    if not valid_choice or not (last_board_state == board_state):
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

        

        class MovesSchema(BaseModel):
            moves: Dict[int, List[int]] = Field(
                ..., description="Mapping from key to list of values"
            )
        class CapturesSchema(BaseModel):
            captures: Dict[int, List[int]] = Field(
                ..., description="Mapping from key to list of values. These should come from either 'normal_captures' or 'dama_captures'"
            )
            model_config = ConfigDict(extra="forbid")

        # temperature=0
        if not (last_board_state == board_state):
            switch = False
        else:
            temperature += 0.04
            if temperature > 1:
                temperature = 0
        while True:

            switch = not switch
            try:
                print("Rerun with temp:", temperature, "is_capture:", is_capture, "results:", results)
                move_llm_3_1 = ChatOllama(
                    model="llama3.1:8b-instruct-fp16",
                    temperature=temperature,
                    format=MovesSchema.model_json_schema(),
                )
                move_llm_3_2 = ChatOllama(
                    model="llama3.2:3b-instruct-fp16",
                    temperature=temperature,
                    format=MovesSchema.model_json_schema(),
                )

                capture_llm_3_1 = ChatOllama(
                    model="llama3.1:8b-instruct-fp16",
                    temperature=temperature,
                    format=CapturesSchema.model_json_schema(),
                )
                capture_llm_3_2 = ChatOllama(
                    model="llama3.2:3b-instruct-fp16",
                    temperature=temperature,
                    format=CapturesSchema.model_json_schema(),
                )

                if is_capture:
                    file_exists = os.path.isfile(results_to_capture_chain)
                    with open(results_to_capture_chain, mode='a', newline='') as file:
                        writer = csv.writer(file)                        
                        if not file_exists:
                            writer.writerow(['results'])
                        writer.writerow([results])

                    if switch:
                        print("Using LLaMa 3.1")
                        capture_chain = capture_template | capture_llm_3_1
                    else:
                        print("Using LLaMa 3.2")
                        capture_chain = capture_template | capture_llm_3_2

                    # response = determiner_chain.invoke({
                    #     "results": results,
                    # })
                    # print("Determiner:", response.content.rstrip())
                    response = capture_chain.invoke({
                        "results": results
                    })
                    
                else:
                    file_exists = os.path.isfile(results_to_move_chain)
                    with open(results_to_move_chain, mode='a', newline='') as file:
                        writer = csv.writer(file)                        
                        if not file_exists:
                            writer.writerow(['results'])
                        writer.writerow([results])
                    
                    if switch:
                        print("Using LLaMa 3.1")
                        move_chain: dict = move_template | move_llm_3_1
                    else:
                        print("Using LLaMa 3.2")
                        move_chain: dict = move_template | move_llm_3_2

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
                # chosen_list = random.choice(src_dest_pairs)
                # chosen_piece_src = chosen_list[0]
                # chosen_piece_dest = chosen_list[1]

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
                                destop = "//" if destop == "/" else destop
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
                elif src_dest_pairs == []:
                    raise Exception("Sorry, no sulod") 
                break
            except Exception as e:
                print("Resultstovaliderror", e)
                temperature += 0.04
                if temperature > 1:
                    temperature = 0
                else:
                    continue



        # print("CHOICE:", chosen_piece_src, chosen_piece_dest)
        last_board_state = board_state
        valid_choice_pairs = src_dest_pairs
    print("CHECK NI IF MAG 503 nsd", valid_choice_pairs, valid_choice)
    while valid_choice_pairs != []:
        print("\nSource-Destination Pairs:", valid_choice_pairs)
        print("Temperature in valid_choice_pairs:", temperature)
        
        llm_best_choice = ChatOllama(
            model="llama3.1:8b-instruct-fp16",
            temperature=.5,
            format="json"
        )

        best_move_prompt = ChatPromptTemplate.from_template(
        """System Prompt:
        You are a Damath game-playing agent that understands the board state representation.
        The game state is provided as a JSON format where the value is a list of square objects.
        Each square object has:
            - \"position\": a two-element list [index, operator], where index ∈ [0,63] is the board coordinate in row-major order and operator ∈ {{'*','/','-','+'}} denotes the arithmetic operator on that square.
            - \"piece\": either null if empty, or a three-element list [color, value, is_dama], where:
                * color ∈ {{'red','blue'}}
                * value is an integer (positive or negative) representing the piece's numeric value
                * is_dama is a boolean indicating king status

        The valid_moves list is a source-destination list with a pair indices [[source, dest], [source, dest]].

        **Normal Move Priorities:**
        1. Advancing toward the opponent’s back rank (especially pieces near promotion at index 63).
        2. Protecting high-value pieces (value indicates risk level).
        3. Controlling central or strategic squares.
        4. Setting up future captures or blocking opponent runs.

        **Dama/King Considerations:**
        - Use Dama moves only if a clear positional or material advantage outweighs a normal advance.
        - Damas may traverse multiple empty squares; simulate landing spots for positioning.

        **Strategic Layer:**
        - Threat Analysis: Avoid leaving the moved piece immediately capturable.
        - Multi-Ply Forecast: Internally look 2–3 plies ahead to avoid traps.
        - Balance material gain vs. positional strength and promotion potential.

        **Output:**
        Return only a JSON object with keys:
        {{
        \"source\": <int>,
        \"destination\": <int>,
        \"reason\": <string>
        }}
        The reason should reference positional strategy (advancement, protection, control).

        Your turn—select the optimal normal move and output JSON only.
        """
        )

        best_capture_prompt = ChatPromptTemplate.from_template(
        """System Prompt:
        You are a Damath game-playing agent that understands the board state representation.
        The game state is provided as a JSON format where the value is a list of square objects.
        Each square object has:
            - \"position\": a two-element list [index, operator], where index ∈ [0,63] is the board coordinate in row-major order and operator ∈ {{'*','/','-','+'}} denotes the arithmetic operator on that square.
            - \"piece\": either null if empty, or a three-element list [color, value, is_dama], where:
                * color ∈ {{'red','blue'}}
                * value is an integer (positive or negative) representing the piece's numeric value
                * is_dama is a boolean indicating king status

        Choose from the valid_moves list maps source positions to a list of triples [source, destination, score].

        **Capture Selection Rules:**
        1. Normal captures occur at offsets +14, -14, +18, -18. After moving to a capture destination, assess whether additional captures are possible from that new square.
        2. Automatically choose the single capture with the highest positive score, avoid negative scores you will lose some points.
        3. For Dama pieces, consider multi-step capture chains: captures may still occur at offsets ±14 and ±18, including longer jumps where the offset is a multiple of 14 (i.e., 7*2) or 18 (i.e., 9*2) to maximize total score.
        4. Perform full internal chain-of-thought; do not reveal it.

        **Output:**
        Return only a JSON object with keys:
        {{
        \"source\": <int>,
        \"destination\": <int>,
        \"reason\": <string>
        }}
        The reason should reference the capture score and the sequence rationale.

        Your turn—select the best capture and output JSON only.
        """
        )

        
        user_prompt = ChatPromptTemplate.from_template(
        """
        User Prompt:
            Given the current board state and valid moves,
            choose the best move and explain your reasoning.
            Board state: {board_state}
            Valid moves: {valid_moves}
        """
        )

        is_capture = False
        for i in valid_choice_pairs:
            if isinstance(i, tuple):
                is_capture = True

        if is_capture:
            chain = best_capture_prompt + user_prompt | llm_best_choice
        else:
            chain = best_move_prompt + user_prompt | llm_best_choice

        response = chain.invoke({
        "board_state": request.jsonboard,
        "valid_moves": valid_choice_pairs,
        })

        response = json.loads(response.content)
        print(response)
        source = response['source']
        destination = response['destination']
        reason = response['reason']
        print(response)
        
        valid_choice = False
        
        temperature += 0.06
        if temperature > 1:
            temperature = 0
        if valid_choice_pairs == []:
            print("Empty na cya")
            source = 1
            destination = 1
            reason = "ERROR"
            valid_choice = False
            break

        for index, item in enumerate(valid_choice_pairs):
            if [item[0], item[1]] == [source, destination]:
                valid_choice = True
                break

        if not valid_choice:
            continue
        else:
            break
    try:
        print("BEFORE:", valid_choice, source,destination)
    except Exception as e:
        print("ERROR SA WALA ANG VALID MOVE:", e)
        print(valid_choice)
    if valid_choice_pairs == [] and valid_choice == True:
        print("Empty na cya")
        source = 1
        destination = 1
        reason = "ERROR"
        valid_choice = False
    elif valid_choice_pairs != []:
        valid_choice_pairs.pop(index)

    
    print(valid_choice, source,destination)
    return {"source": source, "destination": destination, "reason": reason}