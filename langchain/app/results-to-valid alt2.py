from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json
import sys 
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



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
            from utilities.normal_moves import func1, Piece
            import utilities.normal_moves
            new_board = reinitialize_board(board_state, Piece)
            utilities.normal_moves.board_state = new_board
            result = func1(new_board)
        elif test_name == "dama_moves":
            from utilities.dama_moves import func1, Piece
            import utilities.dama_moves
            new_board = reinitialize_board(board_state, Piece)
            utilities.dama_moves.board_state = new_board
            result = func1(new_board)
        elif test_name == "normal_captures":
            from utilities.normal_captures import func5, Piece
            import utilities.normal_captures
            new_board = reinitialize_board(board_state, Piece)
            utilities.normal_captures.board_state = new_board
            result = func5(new_board)
        elif test_name == "dama_captures":
            from utilities.dama_captures import func7, Piece
            import utilities.dama_captures
            new_board = reinitialize_board(board_state, Piece)
            utilities.dama_captures.board_state = new_board
            result = func7(new_board)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

results = {}
for test in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
    new_board_state = [[None, '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', 
              [Piece('r', -11, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X', 
              [Piece('r', 6, is_dama=True), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 
              'X', [None, '/'], 'X', [None, '*'], [Piece('b', 0, is_dama=True), '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', 
              [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X', [None, '-'], [Piece('r', -5, is_dama=True), 
              '-'], 'X', [None, '+'], 'X', [None, '*'], 'X', [None, '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 
              'X', [None, '*']]
    
    results[test] = get_valid_moves(test, new_board_state)

print("\n\nOriginal results:")
print(results)

def clean_dict(data):
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned_value = clean_dict(value)
            if cleaned_value:  # only add if not empty
                cleaned[key] = cleaned_value
            # elif key in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
            #     cleaned[key] = {}
        return cleaned
    elif isinstance(data, list):
        cleaned_list = [clean_dict(item) for item in data if item not in ([], ())]
        return [item for item in cleaned_list if item != {}]  # remove empty dicts
    elif isinstance(data, tuple):
        cleaned_tuple = tuple(item for item in data if item not in ([], ()))
        return cleaned_tuple if cleaned_tuple else None
    return data


# Clean it
results = clean_dict(results)

print("\n\nCleaned results:")
print(results)

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

determiner_template = ChatPromptTemplate.from_template("""
You are given a dictionary named "results". Follow the steps provided.

If the "dama_captures" key is present, keep the key and their values, removing other keys (such as "normal_captures", "normal_moves" and/or "dama_moves").
Else, if "normal_captures" key is present but not "dama_captures", keep the "normal_captures" key, removing other keys (such as "normal_moves" and/or "dama_moves").

Here is the results dictionary:
{results}

Return a Python dictionary ONLY in string format.                                                 

""")

capture_template = ChatPromptTemplate.from_template("""
You are given a dictionary named "results" that contains either only two keys: "normal_captures" and "dama_captures".

Each of these keys maps to a dictionary:
- In "normal_captures", keys are integers, and values are lists of integers.
- In "dama_captures", keys are integers, and values are lists of tuples of integers.

Your task is:
1. Ignore the top-level keys ("normal_captures" and "dama_captures") and work only with their inner dictionaries.
2. Choose one of the two inner dictionaries:
     - If "dama_captures" has a value aside from an empty dictionary, flatten the tuples in the value, and keep this value as the remaining dictionary.
     - Else, keep the "normal_captures" value which is a dictionary.
3. The final result should be a JSON object with a single key "captures", whose value is the remaining dictionary.
4. All keys in the final dictionary should be strings.

Here is the results dictionary:
{results}

Return only the final JSON with key "captures".
""")


llm = ChatOllama(
    model="llama3.1:8b-instruct-fp16",
    temperature=0,
    format="json",
)

if is_capture:

    determiner_chain = determiner_template | llm 
    capture_chain = capture_template | llm

    response = determiner_chain.invoke({
        "results": results,
    })

    response = capture_chain.invoke({
        "results": response.content.rstrip()
    })
else:
    move_chain = move_template | llm

    response = move_chain.invoke({
        "results": results,
    }) 

# filtered_results = json.loads(response_part1.content)
filtered_results = response.content
print("\n\nFiltered (Intermediate) Results:")
print(filtered_results, type(filtered_results))

# parser_prompt_part2 = ChatPromptTemplate.from_template("""
# You are provided with a filtered dictionary named "filtered_results" that contains either capture data (with keys "normal_captures" and "dama_captures")
# or move data (with keys "normal_moves" and "dama_moves").

# Perform the following steps:
# 1. For each key present in the dictionaries:
#    - If "filtered_results" contains capture data:
#       a. If both "normal_captures" and "dama_captures" have non-empty values, use the values from "dama_captures" only.
#       b. If only one dictionary has a non-empty value for that key, use that value.
#       c. Remove the keys "normal_captures" and "dama_captures"
#    - Otherwise, if "filtered_results" contains move data:
#       a. Keep the value ONLY of the "dama_moves" key.
#       b. With the value of the "normal_moves", get the key-value pairs and add it to the value of the "dama_moves" UNLESS the key already exists in the "dama_moves".
#       c. Let's call this the "merged data". Remove the keys "normal_moves" and "dama_moves".
# 2. Return the final JSON output with:
#    - If the input was capture data, return {{{{"captures": {{ ...merged data... }}}}}}
#    - If the input was move data, return {{{{"moves": {{ ...merged data... }}}}}}
#    - 

# Here are the filtered_results:
# {filtered_results}

# Remember: Return the final JSON output ONLY. Do not return a code. 
# """)


# results_to_valid_llm_part2 = ChatOllama(
#     model="llama3.2:3b-instruct-fp16",
#     temperature=0,
#     format="json",    
# )

# chain_part2 = parser_prompt_part2 | results_to_valid_llm_part2

# response_part2 = chain_part2.invoke({
#     "filtered_results": filtered_results,
# })


# final_results = re.sub(r"<think>.*?</think>\n?", "", response_part2.content, flags=re.DOTALL)
# print(final_results)

import ast

# final_results = ast.literal_eval(final_results)

final_results = json.loads(filtered_results)
valid_moves = final_results
print("Final Valid Moves:")
print(valid_moves)





### For capture scoring

# valid_moves = {
#     "captures": {
#             59: [(41, 32)]
#     }
# }


# Get pairings next:
src_dest_pairs = []
is_capture = False
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
print("\n\n\n")
print("SRCDEST pairs:", src_dest_pairs)

if src_dest_pairs != [] and is_capture:
# use the board state to determine score for pairs.
# first, determine the distance


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
            if isinstance(new_board_state[middle][0], Piece):

                if new_board_state[middle][0].color == 'b':
                    enemy = True
                    break
        if enemy:
            try:
                srcval = new_board_state[source][0].value
                midval = new_board_state[middle][0].value
                destop = new_board_state[dest][1]
                print(f"{srcval}{destop}{midval}")
                score = round(eval(f"{srcval}{destop}{midval}"))
                capturing_is_dama = new_board_state[source][0].is_dama
                captured_is_dama = new_board_state[middle][0].is_dama
                if capturing_is_dama and captured_is_dama:
                    score *= 4
                elif capturing_is_dama or captured_is_dama:
                    score *= 2
            except ZeroDivisionError:
                score = 0

            src_dest_pairs[index] = (source, dest, score)

    print(src_dest_pairs)




