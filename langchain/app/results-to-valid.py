from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json


import re




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
            from normal_moves import func1, Piece
            import normal_moves
            new_board = reinitialize_board(board_state, Piece)
            normal_moves.board_state = new_board
            result = func1(new_board)
        elif test_name == "dama_moves":
            from dama_moves import func1, Piece
            import dama_moves
            new_board = reinitialize_board(board_state, Piece)
            dama_moves.board_state = new_board
            result = func1(new_board)
        elif test_name == "normal_captures":
            from normal_captures import func5, Piece
            import normal_captures
            new_board = reinitialize_board(board_state, Piece)
            normal_captures.board_state = new_board
            result = func5(new_board)
        elif test_name == "dama_captures":
            from dama_captures import func7, Piece
            import dama_captures
            new_board = reinitialize_board(board_state, Piece)
            dama_captures.board_state = new_board
            result = func7(new_board)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

results = {}
for test in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
    new_board_state = board_state = [
    [Piece('r', -112, is_dama=False), '*'],
    'X',
    [None, '/'],
    'X',
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    'X',
    [Piece('b', 0, is_dama=False), '/'],
    'X',
    [None, '*'],
    'X',
    [None, '+'],
    'X',
    [None, '-'],
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    [None, '*'],
    'X',
    [Piece('r', -9, is_dama=False), '/'],
    'X',
    'X',
    [None, '+'],
    'X',
    [Piece('b', -11, is_dama=False), '-'],
    'X',
    [None, '/'],
    'X',
    [None, '*'],
    [Piece('b', 0, is_dama=False), '*'],
    'X',
    [Piece('r', -5, is_dama=True), '/'],
    'X',
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    'X',
    [None, '/'],
    'X',
    [Piece('b', -5, is_dama=True), '*'],
    'X',
    [None, '+'],
    'X',
    [None, '-'],
    [None, '-'],
    'X',
    [None, '+'],
    'X',
    [None, '*'],
    'X',
    [Piece('b', 6, is_dama=False), '/'],
    'X',
    'X',
    [None, '+'],
    'X',
    [None, '-'],
    'X',
    [None, '/'],
    'X',
    [Piece('r', 6, is_dama=False), '*']
]
    
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


# Clean it
results = clean_dict(results)

print("\n\nCleaned results:")
print(results)


# parser_prompt_part1 = ChatPromptTemplate.from_template("""
# You are given a dictionary named "results" with the following keys:
# - move data: "normal_moves" and "dama_moves"
# - capture data: "normal_captures" and "dama_captures"

# Your task is to choose which set of data to return.

# Steps:
# 1. For each key in "normal_captures" and "dama_captures":
#     - A list is considered empty if it has no elements.
#     - If the list has elements, consider it empty if every element in the list is an empty tuple (a tuple with zero elements).
# 2. If any key in either capture dictionary has a list that is not empty (by the above rules), choose the capture data.
# 3. Otherwise, if all keys in both capture dictionaries are empty, choose the move data.

# Return a JSON result using the original data without any filtering, in one of the following forms:

# If capture data is chosen:
# {{
#     "captures": {{
#         "normal_captures": {{ ... original normal_captures ... }},
#         "dama_captures": {{ ... original dama_captures ... }}
#     }}
# }}

# If move data is chosen:
# {{
#     "moves": {{
#         "normal_moves": {{ ... original normal_moves ... }},
#         "dama_moves": {{ ... original dama_moves ... }}
#     }}
# }}

# For example, given these results:
# {results}

# Return a JSON result.
# """)

parser_prompt_part1 = ChatPromptTemplate.from_template("""
You are given a dictionary named "results" with a classification for the following keys:
1. "normal_moves" and "dama_moves" dictionaries belong to 'move data', while
2. "normal_captures" and "dama_captures" dictionaries belong to 'capture data'

Your task is to choose which set of data to return.

Steps:
1. If any key in either capture dictionary is not empty, choose the capture data.
2. Otherwise, if all dictionaries in both capture dictionaries are empty, choose the move data.

Return a JSON result using the original data without any filtering, in one of the following forms:

If capture data is chosen:
{{
    "captures": {{
        "normal_captures": {{ ... original normal_captures ... }},
        "dama_captures": {{ ... original dama_captures ... }}
    }}
}}

If move data is chosen:
{{
    "moves": {{
        "normal_moves": {{ ... original normal_moves ... }},
        "dama_moves": {{ ... original dama_moves ... }}
    }}
}}

The original dictionaries must be followed strictly.

For example, given these results:
{results}

REMEMBER: Return a pure-JSON format result ONLY. Do NOT return in a markdown-style code block format.
""")



results_to_valid_llm_part1 = ChatOllama(
    model="gemma3:12b-it-q8_0",
    temperature=0,
    format="json"
)

chain_part1 = parser_prompt_part1 | results_to_valid_llm_part1

response_part1 = chain_part1.invoke({
    "results": results,
})

print(response_part1.content)
filtered_results = json.loads(response_part1.content)
print("\n\nFiltered (Intermediate) Results:")
print(filtered_results)

parser_prompt_part2 = ChatPromptTemplate.from_template("""
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
   - If the input was capture data, return {{{{"captures": {{ ...merged data... }}}}}}
   - If the input was move data, return {{{{"moves": {{ ...merged data... }}}}}}

Here are the filtered_results:
{filtered_results}

Remember: Return the final JSON output ONLY. Do not return a code. 
""")


results_to_valid_llm_part2 = ChatOllama(
    model="deepseek-r1:8b-llama-distill-q8_0",
    temperature=0,
    
)

chain_part2 = parser_prompt_part2 | results_to_valid_llm_part2

response_part2 = chain_part2.invoke({
    "filtered_results": filtered_results,
})


final_result = re.sub(r"<think>.*?</think>\n?", "", response_part2.content, flags=re.DOTALL)

final_results = json.loads(final_result)
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




