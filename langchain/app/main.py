import subprocess
import json
import re
from subprocess import check_output
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

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
            elif key in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
                cleaned[key] = {}
        return cleaned
    elif isinstance(data, list):
        cleaned_list = [clean_dict(item) for item in data if item not in ([], ())]
        return [item for item in cleaned_list if item != {}]  # remove empty dicts
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

    # Process each test condition.
    results = {}
    # Using the provided board state for each test.
    for test in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
        results[test] = get_valid_moves(test, board_state)

    # Clean the results from any empty dictionaries.
    results = clean_dict(results)

    # ----- PART 1: Choose which set of data to return -----
    parser_prompt_part1 = ChatPromptTemplate.from_template(
        """
You are given a dictionary named "results" with a classification for the following keys:
1. "normal_moves" and "dama_moves" dictionaries belong to 'move data', while
2. "normal_captures" and "dama_captures" dictionaries belong to 'capture data'

Your task is to choose which set of data to return.

Steps:
1. If any key in either capture dictionary is not empty, choose the capture data.
2. Otherwise, if all dictionaries in both capture dictionaries are empty, choose the move data.

Return a JSON result using the original data without any filtering, in one of the following forms:

If capture data is chosen:
{
    "captures": {
        "normal_captures": { ... original normal_captures ... },
        "dama_captures": { ... original dama_captures ... }
    }
}

If move data is chosen:
{
    "moves": {
        "normal_moves": { ... original normal_moves ... },
        "dama_moves": { ... original dama_moves ... }
    }
}

The original dictionaries must be followed strictly.

For example, given these results:
{results}

REMEMBER: Return a pure-JSON format result ONLY. Do NOT return in a markdown-style code block format.
"""
    )

    results_to_valid_llm_part1 = ChatOllama(
        model="gemma3:12b-it-q8_0",
        temperature=0,
        format="json"
    )

    chain_part1 = parser_prompt_part1 | results_to_valid_llm_part1

    response_part1 = chain_part1.invoke({
        "results": results,
    })

    try:
        filtered_results = json.loads(response_part1.content)
    except Exception as e:
        return {"status": "error", "error": "Failed to parse chain part 1 response."}

    # ----- PART 2: Process the filtered results -----
    parser_prompt_part2 = ChatPromptTemplate.from_template(
        """
You are provided with a filtered dictionary named "filtered_results" that contains either capture data (with keys "normal_captures" and "dama_captures")
or move data (with keys "normal_moves" and "dama_moves").

Perform the following steps:
1. For each key present in the dictionaries:
   - If "filtered_results" contains capture data:
      a. If both "normal_captures" and "dama_captures" have non-empty values, use the values from "dama_captures" only.
      b. If only one dictionary has a non-empty value for that key, use that value.
   - Otherwise, if "filtered_results" contains move data:
      a. Keep the value ONLY of the "dama_moves" key.
      b. With the value of the "normal_moves", get the key-value pairs and add it to the value of the "dama_moves" UNLESS the key already exists in the "dama_moves".
      c. Let's call this the "merged data".
      d. Remove the "dama_moves" key, because "merged_data" will be used in the next step.
2. Return the final JSON output with:
   - If the input was capture data, return {"captures": { ...merged data... }}
   - If the input was move data, return {"moves": { ...merged data... }}

Here are the filtered_results:
{filtered_results}

Remember: Return the final JSON output ONLY. Do not return a code.
"""
    )

    results_to_valid_llm_part2 = ChatOllama(
        model="deepseek-r1:8b-llama-distill-q8_0",
        temperature=0,
    )

    chain_part2 = parser_prompt_part2 | results_to_valid_llm_part2

    response_part2 = chain_part2.invoke({
        "filtered_results": filtered_results,
    })

    final_result = re.sub(r"<think>.*?</think>\n?", "", response_part2.content, flags=re.DOTALL)

    try:
        final_results = json.loads(final_result)
    except Exception as e:
        return {"status": "error", "error": "Failed to parse chain part 2 response."}

    valid_moves = final_results
    print("Final Valid Moves:")
    print(valid_moves)

    # ----- Convert the valid moves into source-destination pairs -----
    src_dest_pairs = []
    is_capture = False
    for key, value in valid_moves.items():
        try:
            value_converted = {int(k): eval(v) if isinstance(v, str) else eval(str([eval(str(i)) for i in v]))
                               for k, v in value.items()}
        except Exception as e:
            value_converted = value
        if key == 'captures':
            is_capture = True
        for source, destinations in value_converted.items():
            if isinstance(destinations, (list, tuple)):
                for destination in destinations:
                    if isinstance(destination, (tuple, list)):
                        for item in destination:
                            src_dest_pairs.append([source, item])
                    else:
                        src_dest_pairs.append([source, destination])
            else:
                src_dest_pairs.append([source, destinations])

    if src_dest_pairs and is_capture:
        for index, (source, dest) in enumerate(src_dest_pairs):
            distance = dest - source
            directions = [-7, -9, 7, 9]
            direction = None
            factor = None
            for dir_opt in directions:
                if distance % dir_opt == 0:
                    factor = distance // dir_opt
                    direction = abs(dir_opt)
                    break
            enemy = False
            middle = source
            while middle != dest and direction is not None:
                middle += direction
                if isinstance(board_state[middle][0], dict):
                    if board_state[middle][0].get('color') == 'b':
                        enemy = True
                        break
            if enemy:
                try:
                    srcval = board_state[source][0]['value']
                    midval = board_state[middle][0]['value']
                    destop = board_state[dest][1]
                    score = round(eval(f"{srcval}{destop}{midval}"))
                    capturing_is_dama = board_state[source][0].get('is_dama', False)
                    captured_is_dama = board_state[middle][0].get('is_dama', False)
                    if capturing_is_dama and captured_is_dama:
                        score *= 4
                    elif capturing_is_dama or captured_is_dama:
                        score *= 2
                except ZeroDivisionError:
                    score = 0
                src_dest_pairs[index] = (source, dest, score)

    return {"src_dest_pairs": src_dest_pairs}
