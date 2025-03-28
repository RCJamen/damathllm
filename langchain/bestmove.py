from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional

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
    model="llama3.1",
    temperature=0.5,
    format="json"
)

# system_prompt = ChatPromptTemplate.from_template(
#     """System Prompt:
# You are a Damath game-playing agent that understands the board state representation.
# The board is represented as a one-dimensional list of 64 elements (an 8x8 grid). Playable squares are lists of two elements:
#   - The first element is either a Piece (with attributes like color, value, and is_dama) or None if the square is empty.
#   - The second element is an operator (such as '', '/', '-', '+').
# Non-playable squares are denoted by "X".

# How to choose source and destination:
# 1. The valid_moves dictionary shows which pieces can move where:
#    - Keys (source): The position of your moveable pieces.
#    - Values (destinations): For normal pieces, the destinations are provided as a list of integer positions. For Dama/King pieces, the destinations are provided as a tuple (or tuple of tuples). For example:
#     {{
#     18: [(25,), (27, 36, 45, 54, 63), (11, 4)],
#     22: [29, 31],
#     }}
#     - Moves for key 22 are normal piece.
#     - Moves for key 18 (which are tuples) are for Dama/King pieces, so avoid using these moves casually unless a capture or significant strategic advantage is available.

# 2. For normal moves (non-captures) using normal pieces:
#    - Choose a source position from the valid_moves keys with integer list values.
#    - Pick a destination from the list of possible moves for that source.
#    - Also, prefer moves that:
#      * Advance pieces toward the opponent's side.
#      * Protect your valuable pieces.
#      * Control important board positions.
#      * Create opportunities for future captures.
#    - **Prioritize moves that advance normal pieces**, especially those that are near the position value of 63 to attain Dama/King status (closer to the opponent's side).

# 3. For moves involving Dama/King pieces:
#    - The valid_moves entries that have tuple values represent Dama/King moves.
#    - **Avoid using Dama/King moves casually.** Reserve these moves primarily for capturing opportunities or when a clear strategic advantage is present.

# 4. Assessing the Move Consequences:
#    - **Simulate the Outcome:** Before finalizing a move, update the board mentally (or via simulation) to see how it will change.
#    - **Threat Analysis:** Check if moving to the target square exposes your piece to an immediate capture (for example, if moving to a square allows an opponent to capture it immediately). Evaluate the material and positional loss in such scenarios.
#    - **Risk vs. Reward:** Weigh the benefits of the move (advancing position, control, or creating capture opportunities) against the risks (such as exposing a piece to capture or a counter-attack).
#    - **Look-Ahead:** If possible, simulate a few moves ahead (using a minimax-like approach) to foresee potential responses by your opponent and ensure that the move does not lead to a significant disadvantage.

# 5. **Chain-of-Thought Requirement:**
#    - Internally, simulate a chain-of-thought that explains your move evaluation step by step. However, only return the final decision (source, destination, and a succinct explanation) in JSON.
#    - Include an internal evaluation of possible outcomes, but do not output this chain-of-thought in your final answer.

# Return your decision as JSON with three keys: "source", "destination", and "reason".
# """
# )

system_prompt = ChatPromptTemplate.from_template(
    """System Prompt:
You are a Damath game-playing agent that understands the board state representation.
The board is a one-dimensional list of 64 elements (an 8x8 grid). Playable squares are lists of two elements:
  - The first element is either a Piece (with attributes like color, value, and is_dama) or None if the square is empty.
  - The second element is an operator (such as '', '/', '-', '+').
Non-playable squares are denoted by "X".

Instructions for choosing moves:
1. Valid Moves:
   - The valid_moves dictionary maps source positions to destination positions.
   - For normal pieces, destinations are provided as a list of integers.
   - For Dama/King pieces, destinations
   are provided as tuples (or tuples of tuples).
   - Example:
     {{
       18: [(25,), (27, 36, 45, 54, 63), (11, 4)],
       22: [29, 31],
     }}
   - Use Dama moves (tuple values) only for capturing opportunities or when a clear strategic advantage is present.

2. Normal Moves (Non-captures):
   - Select a source position from valid_moves with list values.
   - Choose a destination from the list.
   - Prioritize moves that:
       * Advance pieces toward the opponent's side.
       * Protect valuable pieces.
       * Control key board positions.
       * Create opportunities for future captures.
   - Emphasize advancing normal pieces, especially those nearing position 63 to attain Dama/King status.

3. Dama/King Moves:
   - Reserve these moves for capturing or when a significant strategic advantage is available.

4. Enhanced Strategy Considerations:
   - **Anticipate Opponent's Moves:** Internally simulate possible opponent responses to avoid moves that expose your pieces to immediate counter-attacks.
   - **Balance Objectives:** Weigh the benefits of advancing pieces toward Dama status against maintaining a strong defensive position.
   - **Multi-step Planning:** Consider how the move positions you for future turns, including setting up additional captures or forcing the opponent into a weak configuration.
   - **Risk vs. Reward:** Assess both the material and positional gains against the risks of exposing pieces.

5. Evaluating Move Consequences:
   - Simulate the outcome of the move on the board.
   - Perform threat analysis to check for potential immediate captures.
   - Look ahead a few moves (using a minimax-like approach) to ensure the move does not lead to a significant disadvantage.

6. Chain-of-Thought Requirement:
   - Internally simulate your reasoning step-by-step.
   - Only output the final decision in JSON with keys "source", "destination", and "reason".

Return your decision as JSON.
"""
)


user_prompt = ChatPromptTemplate.from_template(
    """User Prompt:
Given the current board state and valid moves,
choose the best move and explain your reasoning.

Board state: {board_state}
Valid moves: {valid_moves}
"""
)

chain = system_prompt + user_prompt | llm


board_state = [[Piece('r', 2, is_dama=False), '*'], 'X', [Piece('r', -5, is_dama=False), '/'], 'X', [Piece('r', 8, is_dama=False), '-'], 'X', [Piece('r', -11, is_dama=False), '+'], 'X', 'X', [Piece('r', -7, is_dama=False), '/'], 'X', [Piece('r', 10, is_dama=False), '*'], 'X', [Piece('r', -3, is_dama=False), '+'], 'X', [Piece('r', 0, is_dama=False), '-'], [Piece('r', 4, is_dama=False), '-'], 'X', [Piece('r', -1, is_dama=False), '+'], 'X', [Piece('r', 6, is_dama=False), '*'], 'X', [Piece('r', -9, is_dama=False), '/'], 'X', 'X', [None, '+'], 'X', [None, '-'], 'X', [None, '/'], 'X', [None, '*'], [None, '*'], 'X', [Piece('b', 6, is_dama=False), '/'], 'X', [None, '-'], 'X', [None, '+'], 'X', 'X', [Piece('b', -9, is_dama=False), '/'], 'X', [None, '*'], 'X', [Piece('b', -1, is_dama=False), '+'], 'X', [Piece('b', 4, is_dama=False), '-'], [Piece('b', 0, is_dama=False), '-'], 'X', [Piece('b', -3, is_dama=False), '+'], 'X', [Piece('b', 10, is_dama=False), '*'], 'X', [Piece('b', -7, is_dama=False), '/'], 'X', 'X', [Piece('b', -11, is_dama=False), '+'], 'X', [Piece('b', 8, is_dama=False), '-'], 'X', [Piece('b', -5, is_dama=False), '/'], 'X', [Piece('b', 2, is_dama=False), '*']]


valid_moves = {
    16: [25],
    18: [25, 27],
    20: [27, 29],
    22: [29, 31],
}


response = chain.invoke({
    "board_state": board_state,
    "valid_moves": valid_moves,
})
