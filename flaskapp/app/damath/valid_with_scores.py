import sys 
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
            from damath.utilities.normal_moves import func1, Piece
            import damath.utilities.normal_moves
            new_board = reinitialize_board(board_state, Piece)
            damath.utilities.normal_moves.board_state = new_board
            result = func1(new_board)
        elif test_name == "dama_moves":
            from damath.utilities.dama_moves import func1, Piece
            import damath.utilities.dama_moves
            new_board = reinitialize_board(board_state, Piece)
            damath.utilities.dama_moves.board_state = new_board
            result = func1(new_board)
        elif test_name == "normal_captures":
            from damath.utilities.normal_captures import func5, Piece
            import damath.utilities.normal_captures
            new_board = reinitialize_board(board_state, Piece)
            damath.utilities.normal_captures.board_state = new_board
            result = func5(new_board)
        elif test_name == "dama_captures":
            from damath.utilities.dama_captures import func7, Piece
            import damath.utilities.dama_captures
            new_board = reinitialize_board(board_state, Piece)
            damath.utilities.dama_captures.board_state = new_board
            result = func7(new_board)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def get_valid_with_scores(Piece, new_board_state):
    print("ERROR GON", type(new_board_state), new_board_state)
    results = {}
    for test in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
        results[test] = get_valid_moves(test, new_board_state)

    print("\n\nOriginal results:")
    print(results)

    board_state = new_board_state

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

    results = clean_dict(results)
    print("\n\nCleaned results:")
    print(results)

    is_capture = False
    if "dama_captures" in results.keys():
        results.pop("normal_captures", None)
        results.pop("normal_moves", None)
        results.pop("dama_moves", None)
        is_capture = True
    elif "normal_captures" in results.keys():
        results.pop("normal_moves", None)
        results.pop("dama_moves", None)
        is_capture = True

    print("\n\nTEMPFILE", results, is_capture)

    valid_moves_val = {}
    valid_moves = {}
    for key, value in results.items():
        valid_moves_val.update(value)

    if is_capture:
        valid_moves.update({"captures": valid_moves_val})
    else:
        valid_moves.update({"moves": valid_moves_val})

    print("Final Valid Moves:")
    print(valid_moves)

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

    print("SRCDEST pairs:", src_dest_pairs)
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
                    print(source, board_state[source])
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

    return src_dest_pairs

