import sys
import signal
from contextlib import contextmanager
from multiprocessing import Process, Queue
import platform

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)

def run_with_timeout(func, args, timeout_seconds):
    q = Queue()
    p = Process(target=lambda: q.put(func(*args)))
    p.start()
    p.join(timeout_seconds)

    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutException("Timed out!")

    return q.get()

def safe_run_test(test_name):
    try:
        if test_name == "normal_moves":
            from normal_moves import func1, board_state
            result = str(func1(board_state))
        elif test_name == "dama_moves":
            from dama_moves import func1, board_state
            result = str(func1(board_state))
        elif test_name == "normal_captures":
            from normal_captures import func5, board_state
            result = str(func5(board_state))
        elif test_name == "dama_captures":
            from dama_captures import func7, board_state
            result = str(func7(board_state))
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def run_specific_test(test_name):
    MAX_EXECUTION_TIME = 5
    try:
        if platform.system() != 'Windows':
            with timeout(MAX_EXECUTION_TIME):
                result = safe_run_test(test_name)
        else:
            result = run_with_timeout(safe_run_test, (test_name,), MAX_EXECUTION_TIME)

        print(f"{test_name.upper()}:{result}")
    except TimeoutException:
        print(f"❌ {test_name.upper()}: Function execution timed out after {MAX_EXECUTION_TIME} seconds")
    except ImportError as e:
        print(f"❌ {test_name.upper()}: Import error - {str(e)}")
    except Exception as e:
        print(f"❌ {test_name.upper()}: Unexpected error - {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_specific_test(sys.argv[1])
    else:
        for test in ["normal_moves", "dama_moves", "normal_captures", "dama_captures"]:
            run_specific_test(test)
