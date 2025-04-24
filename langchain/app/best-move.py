import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

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

llm = ChatOllama(
    model="llama3.1:8b-instruct-fp16",
    temperature=1,
    format="json"
)


# System prompt containing Damath context, rules, and strategies
system_prompt = ChatPromptTemplate.from_template(
    """
System Prompt:
You are an expert Damath game-playing agent. Damath rules and strategic guidelines:

1. **Board & Operators**:
   - Played on the 32 white squares of an 8×8 board, each labeled with one of {{+, -, *, /}}.
   - Men move diagonally forward; Damas (kings) move diagonally any number of empty squares.
   - A man promotes to Dama upon reaching the opponent’s back rank (positions 0 or 63).

2. **Captures & Scoring**:
   - Jump an enemy piece to capture it; apply the landing square’s operator to your piece’s and the captured piece’s values to compute points.
   - Multi-jump sequences allowed. Damas can change direction mid-jump.
   - **Forced Captures**: If any capture exists, it must be taken. Select the sequence with the highest total score.

3. **Non-Capture Moves** (only when no captures available):
   - Advance men toward promotion.
   - Protect high-value pieces (avoid immediate recapture).
   - Control center/strategic diagonals.
   - Plan 2–3 plies ahead to avoid traps.

4. **Move Input**:
   - The input JSON has keys:
     * "board": list of 32 squares, each with:
       - "position": [index, operator]
       - "piece": null or [color, value, is_dama]
     * "valid_moves": a list where each element is either:
       - [src, dst] for a normal move
       - [src, dst, score] for a capturing move

5. **Decision Logic**:
   1. Scan valid_moves for any captures (length 3 entries). If found, pick the entry/triple with the highest score. Allow multi-step Dama captures if listed.
   2. If no captures, evaluate all [src, dst] pairs by:
      - Promotion potential (higher index toward back rank).
      - Safety (landing square not immediately capturable).
      - Positional control (center/diagonals).

6. **Output**:
   - Return exactly one JSON object with:
     {{
       "source": <int>,
       "destination": <int>,
       "reason": <string>
     }}
   - The reason should cite the criterion.
"""
)



user_prompt = ChatPromptTemplate.from_template(
    """
User Prompt:
Given the current board state and valid_moves list,
choose the optimal Damath move.

Board: {board_state}
Valid moves: {valid_moves}
"""
)


chain = system_prompt + user_prompt | llm


board_state ='{"board":[{"piece":["red",2,false],"position":[0,"*"]},{"piece":["red",-5,false],"position":[2,"/"]},{"piece":["red",8,false],"position":[4,"-"]},{"piece":["red",-11,false],"position":[6,"+"]},{"piece":["red",-7,false],"position":[9,"/"]},{"piece":["red",10,false],"position":[11,"*"]},{"piece":["red",-3,false],"position":[13,"+"]},{"piece":["red",0,false],"position":[15,"-"]},{"piece":["red",4,false],"position":[16,"-"]},{"piece":["red",-1,false],"position":[18,"+"]},{"piece":["red",6,false],"position":[20,"*"]},{"piece":["red",-9,false],"position":[22,"/"]},{"piece":null,"position":[25,"+"]},{"piece":null,"position":[27,"-"]},{"piece":null,"position":[29,"/"]},{"piece":null,"position":[31,"*"]},{"piece":["blue",-9,false],"position":[32,"*"]},{"piece":null,"position":[34,"/"]},{"piece":null,"position":[36,"-"]},{"piece":null,"position":[38,"+"]},{"piece":null,"position":[41,"/"]},{"piece":["blue",6,false],"position":[43,"*"]},{"piece":["blue",-1,false],"position":[45,"+"]},{"piece":["blue",4,false],"position":[47,"-"]},{"piece":["blue",0,false],"position":[48,"-"]},{"piece":["blue",-3,false],"position":[50,"+"]},{"piece":["blue",10,false],"position":[52,"*"]},{"piece":["blue",-7,false],"position":[54,"/"]},{"piece":["blue",-11,false],"position":[57,"+"]},{"piece":["blue",8,false],"position":[59,"-"]},{"piece":["blue",-5,false],"position":[61,"/"]},{"piece":["blue",2,false],"position":[63,"*"]}]}'

board_state = json.loads(board_state)

valid_moves = [[16, 25], [18, 25], [18, 27], [20, 27], [20, 29], [22, 29], [22, 31]]

print({
    "board_state": board_state,
    "valid_moves": valid_moves,
})

response = chain.invoke({
    "board_state": board_state,
    "valid_moves": valid_moves,
})

print(response.content)