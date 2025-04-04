#!/bin/bash

# Function to check if arrays are equal
check_output() {
    expected="$1"
    actual="$2"
    test_name="$3"

    if [ "$actual" = "$expected" ]; then
        echo "✅ $test_name test passed"
        return 0
    else
        echo "❌ $test_name test failed"
        echo "Expected: $expected"
        echo "Got: $actual"
        return 1
    fi
}

# Create test file
cat > test-code-output.py << 'EOF'
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
EOF

# Expected outputs
EXPECTED_NORMAL_MOVES="{0: [], 2: [], 4: [], 6: [], 9: [], 11: [], 13: [], 15: [], 16: [25], 18: [25, 27], 20: [27, 29], 22: [29, 31]}"
EXPECTED_DAMA_MOVES="{20: [(27, 34, 41), (29, 38, 47), (11, 2)], 48: [(57,), (41, 34, 27)]}"
EXPECTED_NORMAL_CAPTURES="{0: [18], 22: [], 34: [52, 20], 63: [45]}"
EXPECTED_DAMA_CAPTURES="{34: [(), (52, 61), (20, 13, 6), ()]}"

# First generate all code files
echo "Generating initial code files..."
# python3 code-generator-langchain.py

# Initialize status arrays
declare -A test_status
test_status["normal_moves"]=false
test_status["dama_moves"]=false
test_status["normal_captures"]=false
test_status["dama_captures"]=false

while true; do
    # Run tests
    echo "Running tests..."

    # Test each component and regenerate if failed
    for test in "${!test_status[@]}"; do
        if ! ${test_status[$test]}; then
            echo "Testing $test..."
            result=$(python3 test-code-output.py "$test" | grep "^${test^^}:" | sed 's/^[^{]*{/{/')

            case $test in
                "normal_moves")
                    if check_output "$EXPECTED_NORMAL_MOVES" "$result" "Normal Moves"; then
                        test_status[$test]=true
                    else
                        echo "Regenerating $test..."
                        python3 code-generator-langchain.py "$test"
                    fi
                    ;;
                "dama_moves")
                    if check_output "$EXPECTED_DAMA_MOVES" "$result" "Dama Moves"; then
                        test_status[$test]=true
                    else
                        echo "Regenerating $test..."
                        python3 code-generator-langchain.py "$test"
                    fi
                    ;;
                "normal_captures")
                    if check_output "$EXPECTED_NORMAL_CAPTURES" "$result" "Normal Captures"; then
                        test_status[$test]=true
                    else
                        echo "Regenerating $test..."
                        python3 code-generator-langchain.py "$test"
                    fi
                    ;;
                "dama_captures")
                    if check_output "$EXPECTED_DAMA_CAPTURES" "$result" "Dama Captures"; then
                        test_status[$test]=true
                    else
                        echo "Regenerating $test..."
                        python3 code-generator-langchain.py "$test"
                    fi
                    ;;
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

    echo "Failed tests: $failed_count/4"

    # If all tests pass, exit
    if [ $failed_count -eq 0 ]; then
        echo "All tests passed! 🎉"
        break
    fi

    echo "Waiting before next attempt..."
    sleep 2
done
