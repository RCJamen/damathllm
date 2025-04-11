#!/bin/bash

# Function to check if arrays are equal
check_output() {
    expected="$1"
    actual="$2"
    test_name="$3"

    if [ "$actual" = "$expected" ]; then
        echo "✅ $test_name test passed"
        echo "Expected: $expected"
        echo "Got: $actual"
        return 0
    else
        echo "❌ $test_name test failed"
        echo "Expected: $expected"
        echo "Got: $actual"
        return 1
    fi
}

# Create test file
cat > ../utilities/test-code-output.py << 'EOF'
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
EOF

# Expected outputs
EXPECTED_NORMAL_MOVES="{0: [], 2: [], 4: [], 6: [], 9: [], 11: [], 13: [], 15: [], 16: [25], 18: [25, 27], 20: [27, 29], 22: [29, 31]}"
EXPECTED_DAMA_MOVES="{20: [(27, 34, 41), (29, 38, 47), (11, 2)], 48: [(57,), (41, 34, 27)]}"
EXPECTED_DAMA_MOVES_ALT="{20: [(27, 34, 41), (29, 38, 47), (11, 2), ()], 48: [(), (57,), (), (41, 34, 27)]}"
# EXPECTED_NORMAL_CAPTURES="{0: [18], 22: [], 34: [52, 20], 63: [45]}"
# EXPECTED_DAMA_CAPTURES="{34: [(), (52, 61), (20, 13, 6), ()]}"

# First generate all code files
echo "Generating initial code files..."
# python3 ../utilities/code-generator-langchain.py

# Initialize status arrays
declare -A test_status
test_status["normal_moves"]=false
test_status["dama_moves"]=false
# test_status["normal_captures"]=false
# test_status["dama_captures"]=false

while true; do
    # Run tests
    echo "Running tests..."

    # Test each component and regenerate if failed
    for test in "${!test_status[@]}"; do
        if ! ${test_status[$test]}; then
            echo "Testing $test..."
            result=$(python3 ../utilities/test-code-output.py "$test" | grep "^${test^^}:" | sed 's/^[^{]*{/{/')

            case $test in
                "normal_moves")
                    if check_output "$EXPECTED_NORMAL_MOVES" "$result" "Normal Moves"; then
                        test_status[$test]=true
                    else
                        echo "Regenerating $test..."
                        python3 ../utilities/code-generator-langchain.py "$test"
                    fi
                    ;;
                "dama_moves")
                    if check_output "$EXPECTED_DAMA_MOVES" "$result" "Dama Moves" || check_output "$EXPECTED_DAMA_MOVES_ALT" "$result" "Dama Moves"; then
                        test_status[$test]=true
                    else
                        echo "Regenerating $test..."
                        python3 ../utilities/code-generator-langchain.py "$test"
                    fi
                    ;;
                # "normal_captures")
                #     if check_output "$EXPECTED_NORMAL_CAPTURES" "$result" "Normal Captures"; then
                #         test_status[$test]=true
                #     else
                #         echo "Regenerating $test..."
                #         python3 code-generator-langchain.py "$test"
                #     fi
                #     ;;
                # "dama_captures")
                #     if check_output "$EXPECTED_DAMA_CAPTURES" "$result" "Dama Captures"; then
                #         test_status[$test]=true
                #     else
                #         echo "Regenerating $test..."
                #         python3 code-generator-langchain.py "$test"
                #     fi
                #     ;;
            esac
        fi
    done

    # Count remaining failed tests
    failed_count=0
    for status in "${test_status[@]}"; do
        if ! $status; then
            ((failed_count++))
        fi
    done

    echo "Failed tests: $failed_count/2"

    # If all tests pass, exit
    if [ $failed_count -eq 0 ]; then
        echo "All tests passed! 🎉"
        break
    fi

    echo "Waiting before next attempt..."
    sleep 2
done
