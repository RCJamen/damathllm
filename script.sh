#!/bin/bash
# This script starts the Flask and Uvicorn servers in their respective directories.
# It also traps termination signals so that stopping this script will also stop both servers.

# Function to clean up background processes
cleanup() {
    echo "Stopping services..."
    kill "$flask_pid" "$uvicorn_pid"
    exit 0
}

# Trap SIGINT and SIGTERM (e.g., Ctrl+C)
trap cleanup SIGINT SIGTERM

# Start Flask server in the ./flaskapp directory in the background
(
  cd ./flaskapp || exit
  flask run --debug
) &
flask_pid=$!

# Start Uvicorn server in the ./langchain directory in the background
(
  cd ./langchain || exit
  uvicorn app.main:app --reload
) &
uvicorn_pid=$!

# Wait for both background processes to finish
wait "$flask_pid" "$uvicorn_pid"

