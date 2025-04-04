import sys

from normal_moves import func1 as normal_moves
from dama_moves import func1 as dama_moves
from normal_captures import func5 as normal_captures
from dama_captures import func7 as dama_captures

from normal_moves import board_state as normal_moves_board
from dama_moves import board_state as dama_moves_board
from normal_captures import board_state as normal_captures_board
from dama_captures import board_state as dama_captures_board

def run_specific_test(test_name):
    result = None
    if test_name == "normal_moves":
        result = str(normal_moves(normal_moves_board))
    elif test_name == "dama_moves":
        result = str(dama_moves(dama_moves_board))
    elif test_name == "normal_captures":
        result = str(normal_captures(normal_captures_board))
    elif test_name == "dama_captures":
        result = str(dama_captures(dama_captures_board))
    print(f"{test_name.upper()}:{result}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_specific_test(sys.argv[1])
    else:
        for test in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
            run_specific_test(test)
