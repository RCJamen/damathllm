#!/bin/bash
# This script starts the Flask and Uvicorn servers and sets up the database.

# Function to clean up background processes
cleanup() {
    echo "Stopping services..."
    kill "$flask_pid" "$uvicorn_pid"
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Step 1: Initialize the database schema
echo "Initializing the database..."
python3 setup_database.py

# Step 2: Start Flask server
(
  cd ./flaskapp || exit
  flask run --debug
) &
flask_pid=$!

# Step 3: Start Uvicorn server
(
  cd ./langchain || exit
  uvicorn app.main:app --reload
) &
uvicorn_pid=$!

# Step 4: Wait for both to finish
wait "$flask_pid" "$uvicorn_pid"
