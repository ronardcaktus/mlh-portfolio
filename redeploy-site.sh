#!/bin/bash

# 1. Kill all existing tmux sessions
echo "Stopping all existing tmux sessions..."
tmux kill-server 2>/dev/null

# 2. cd into mlh-portfolio dir
PROJECT_DIR="mlh-portfolio"
echo "Navigating to project directory..."
cd "$PROJECT_DIR" || { echo "Error: Could not enter directory $PROJECT_DIR"; exit 1; }

# 3. Fetch latest changes and hard reset to origin/main
echo "Updating code from GitHub main branch..."
git fetch && git reset origin/main --hard

# 4. Enter the python virtual environment and Install python dependencies
echo "Activating virtual environment and updating dependencies..."
source python3-virtualenv/bin/activate
pip install -r requirements.txt

# 5. Set up environment variables (pushed to this server from the local .envrc by secrets.sh)
echo "Setting up environment variables..."
source .envrc || { echo "Error: .envrc not found. Run ./secrets.sh locally to push secrets to this server."; exit 1; }

# 6. Start a new detached Tmux session and spin up the Flask server
echo "Starting Flask server inside a new detached tmux session..."
tmux new-session -d -s flask-server "cd $(pwd) && source python3-virtualenv/bin/activate && source .envrc && flask run --host=0.0.0.0 2>&1 | tee ~/flask-server.log"

# 7. Verify Flask actually stayed up
sleep 3
if curl -s -m 5 http://localhost:5000 > /dev/null; then
    echo "🚀 Deployment successfully completed!"
    echo "Go to http://rmoon.duckdns.org:5000/"
else
    echo "❌ Flask is not responding. Last log lines:"
    tail -20 ~/flask-server.log
    exit 1
fi