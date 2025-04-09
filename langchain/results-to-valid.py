from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json

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
    new_board_state = [[Piece('r', 2, is_dama=False), '*'], 'X', [None, '/'], 'X', [None, '-'], 'X', [Piece('r', -11, is_dama=False), '+'], 'X', 'X', [Piece('r', -5, is_dama=False), '/'], 'X', [Piece('r', 10, is_dama=False), '*'], 'X', [Piece('r', 8, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [None, '-'], 'X', [None, '+'], 'X', [None, '*'], 'X', [Piece('r', -3, is_dama=False), '/'], 'X', 'X', [Piece('r', -1, is_dama=False), '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], [None, '*'], 'X', [Piece('r', -7, is_dama=False), '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [None, '/'], 'X', [None, '*'], 'X', [None, '+'], 'X', [None, '-'], [None, '-'], 'X', [Piece('b', -11, is_dama=False), '+'], 'X', [None, '*'], 'X', [Piece('b', 2, is_dama=False), '/'], 'X', 'X', [None, '+'], 'X', [Piece('r', 6, is_dama=True), '-'], 'X', [None, '/'], 'X', [None, '*']]

    results[test] = get_valid_moves(test, new_board_state)

print("Original results:")
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
You are given a dictionary named "results" with the following keys:
1. move data: "normal_moves" and "dama_moves"
2. capture data: "normal_captures" and "dama_captures"

Your task is to choose which set of data to return.

Steps:
1. For each key in "normal_captures" and "dama_captures": A list is considered empty if it has no elements. If the list has elements, consider it empty if every element in the list is an empty tuple (a tuple with zero elements).
2. If any key in either capture dictionary has a list that is not empty (by the above rules), choose the capture data.
3. Otherwise, if all keys in both capture dictionaries are empty, choose the move data.

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

For example, given these results:
{results}

Return a JSON result.
""")



results_to_valid_llm_part1 = ChatOllama(
    model="llama3.2:3b-instruct-q8_0",
    temperature=0,
    format="json"
)

chain_part1 = parser_prompt_part1 | results_to_valid_llm_part1

response_part1 = chain_part1.invoke({
    "results": results,
})

filtered_results = json.loads(response_part1.content)
print("Filtered (Intermediate) Results:")
print(filtered_results)

parser_prompt_part2 = ChatPromptTemplate.from_template("""
You are provided with a filtered dictionary named "filtered_results" that contains either capture data (with keys "normal_captures" and "dama_captures")
or move data (with keys "normal_moves" and "dama_moves").

Perform the following steps:
1. For each key present in the dictionaries:
   - If "filtered_results" contains capture data:
      a. For a given key, if both "normal_captures" and "dama_captures" have non-empty values, use the values from "dama_captures" only.
      b. If only one dictionary has a non-empty value for that key, use that value.
   - Otherwise, if "filtered_results" contains move data:
      a. For a given key, merge the lists by taking the values from "normal_moves" and then appending the values from "dama_moves" (assume any tuple values in "dama_moves" are already flattened).
2. After merging, remove any key that has an empty list.
3. Return the final JSON output with:
   - If the input was capture data, return {{{{"captures": {{ ...merged data... }}}}}}
   - If the input was move data, return {{{{"moves": {{ ...merged data... }}}}}}

Here are the filtered_results:
{filtered_results}

Return the final JSON output.
""")


results_to_valid_llm_part2 = ChatOllama(
    model="llama3.1",
    temperature=0,
    format="json"
)

chain_part2 = parser_prompt_part2 | results_to_valid_llm_part2

response_part2 = chain_part2.invoke({
    "filtered_results": filtered_results,
})

final_results = json.loads(response_part2.content)
valid_moves = final_results
print("Final Valid Moves:")
print(valid_moves)
