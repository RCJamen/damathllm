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

# Expected outputs
EXPECTED_NORMAL_MOVES="{0: [], 2: [], 4: [], 6: [], 9: [], 11: [], 13: [], 15: [], 16: [25], 18: [25, 27], 20: [27, 29], 22: [29, 31]}"
EXPECTED_DAMA_MOVES="{20: [(27, 34, 41), (29, 38, 47), (11, 2)], 48: [(57,), (41, 34, 27)]}"
EXPECTED_DAMA_MOVES_ALT="{20: [(27, 34, 41), (29, 38, 47), (11, 2), ()], 48: [(), (57,), (), (41, 34, 27)]}"
EXPECTED_NORMAL_CAPTURES="{0: [18], 22: [], 34: [52, 20], 63: [45]}"
EXPECTED_DAMA_CAPTURES="{34: [(), (52, 61), (20, 13, 6), ()]}"

# Create test runner
cat > ./utilities/test-code-output.py << 'EOF'
import sys
import signal
from contextlib import contextmanager
from multiprocessing import Process, Queue
import platform

class TimeoutException(Exception): pass

@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame): raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try: yield
    finally: signal.alarm(0)

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
            return str(func1(board_state))
        elif test_name == "dama_moves":
            from dama_moves import func1, board_state
            return str(func1(board_state))
        elif test_name == "normal_captures":
            from normal_captures import func5, board_state
            return str(func5(board_state))
        elif test_name == "dama_captures":
            from dama_captures import func7, board_state
            return str(func7(board_state))
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
        print(f"{test_name.upper()}:TIMEOUT")
    except Exception as e:
        print(f"{test_name.upper()}:ERROR - {str(e)}")

if __name__ == "__main__":
    for test in sys.argv[1:]:
        run_specific_test(test)
EOF

# Define test expectations
declare -A EXPECTED_RESULTS=(
    ["normal_moves"]="$EXPECTED_NORMAL_MOVES"
    ["dama_moves"]="$EXPECTED_DAMA_MOVES|$EXPECTED_DAMA_MOVES_ALT"
    ["normal_captures"]="$EXPECTED_NORMAL_CAPTURES"
    ["dama_captures"]="$EXPECTED_DAMA_CAPTURES"
)

# Initialize all as failed
declare -A test_status
for test in "${!EXPECTED_RESULTS[@]}"; do
    test_status[$test]=false
done

# Function to generate in parallel
generate_tests() {
    for test in "${!test_status[@]}"; do
        if ! ${test_status[$test]}; then
            echo "Regenerating $test..."
            python3 ./utilities/code-generator-langchain.py "$test" &
        fi
    done
    wait
}

# Function to run all tests and gather results
run_tests() {
    echo "Running tests..."
    output=$(python3 ./utilities/test-code-output.py "${!test_status[@]}" | grep -E "^[A-Z_]+:")

    while IFS= read -r line; do
        test_name=$(echo "$line" | cut -d: -f1 | tr '[:upper:]' '[:lower:]')
        result=$(echo "$line" | sed "s/^[^:]*://")
        expected="${EXPECTED_RESULTS[$test_name]}"

        if [[ "$expected" == *"|"* ]]; then
            IFS="|" read -ra options <<< "$expected"
            match=false
            for opt in "${options[@]}"; do
                [[ "$result" == "$opt" ]] && match=true && break
            done
            if $match; then
                echo "✅ $test_name test passed"
                test_status[$test_name]=true
            else
                echo "❌ $test_name test failed"
            fi
        else
            if [[ "$result" == "$expected" ]]; then
                echo "✅ $test_name test passed"
                test_status[$test_name]=true
            else
                echo "❌ $test_name test failed"
            fi
        fi
    done <<< "$output"
}

# Main loop
while true; do
    # Run tests first
    run_tests

    failed_count=0
    for status in "${test_status[@]}"; do
        if ! $status; then
            ((failed_count++))
        fi
    done

    echo "Failed tests: $failed_count"

    if [ $failed_count -eq 0 ]; then
        echo "🎉 All tests passed!"
        break
    fi

    # Only generate new code if tests failed
    echo "Generating new code for failed tests..."
    generate_tests

    echo "Retrying in 2 seconds..."
    sleep 2
done
