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
    temperature=.4,
    format="json"
)


system_prompt = ChatPromptTemplate.from_template(
    """System Prompt:
    You are a Damath game-playing agent that understands the board state representation.
    The game state is provided as a JSON object with a single key "board" whose value is a list of square objects.
    Each square object has:
        - "position": a two-element list [index, operator], where index ∈ [0,63] is the board coordinate in row-major order and operator ∈ {{'*','/','-','+'}} denotes the arithmetic operator on that square.
        - "piece": either null if empty, or a three-element list [color, value, is_dama], where:
            * color ∈ {{'red','blue'}}
            * value is an integer (positive or negative) representing the piece's numeric value
            * is_dama is a boolean indicating king status

    The valid_moves dictionary maps source positions to:
    - For normal moves: a list of destination indices (e.g. [[16, 25], [18, 25], …]).
    - For capture moves: a list of triples [source, destination, score] (e.g. [(43, 29, 0)], [(25, 43, 24)]).

    1. Normal Moves (Non-captures):
    - Consider only when no capture is available.
    - Prioritize:
        • Advancing toward the opponent’s back rank (especially pieces close to promotion at 63).
        • Protecting high-value pieces (higher `value` → higher risk).
        • Controlling central or strategic squares.
        • Setting up future captures or blocking opponent runs.

    2. Capturing Moves (Triples):
    - Always scan valid_moves for any capture triples ([src, dst, score]).
    - Prefer the highest‐scoring capture sequence. If multiple captures are possible, choose the chain yielding maximal total score.
    - Allow Dama (king) pieces to make multi-step captures if available.

    3. Dama/King Moves:
    - Use only for captures or when a clear positional or material advantage outweighs a normal advance.
    - Damas may traverse multiple empty squares; simulate landing spots for both captures and positioning.

    4. Strategic Layer:
    - **Threat Analysis:** After any move, ensure the moved piece isn’t immediately capturable.
    - **Multi-Step Forecast:** Internally look 2–3 plies ahead (minimax-style) to avoid traps.
    - **Balance:** Weigh material gain (capture score) vs. positional strength and promotion potential.

    5. Output:
    - Perform full chain-of-thought internally; do not reveal it.
    - Return **only** a JSON object with keys:
        ```json
        {{ "source": <int>, "destination": <int>, "reason": <string> }}
        ```
    - For captures, the move’s “reason” should mention the capture score and sequence rationale.

    Your turn—select the optimal move and output JSON only."""
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