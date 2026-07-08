#!/bin/bash

# 1. cd into mlh-portfolio dir
PROJECT_DIR="mlh-portfolio"
echo "Navigating to project directory..."
cd "$PROJECT_DIR" || { echo "Error: Could not enter directory $PROJECT_DIR"; exit 1; }

# 2. Fetch latest changes and hard reset to origin/main
echo "Updating code from GitHub main branch..."
git fetch && git reset origin/main --hard

# 3. Enter the python virtual environment and Install python dependencies
echo "Activating virtual environment and updating dependencies..."
source python3-virtualenv/bin/activate
pip install -r requirements.txt

# 4. Make sure the environment variables file is present (the service sources it on start)
echo "Checking environment variables file..."
[ -f .envrc ] || { echo "Error: .envrc not found. Run ./secrets.sh locally to push secrets to this server."; exit 1; }

# 5. Restart the systemd service so Flask picks up the new code
echo "Restarting myportfolio service..."
systemctl restart myportfolio || { echo "Error: Could not restart myportfolio service."; exit 1; }

# 6. Ensure Flask stayed up
sleep 3
if curl -s -m 5 http://localhost:5000 > /dev/null; then
    echo "🚀 Deployment successfully completed!"
    echo "Go to http://rmoon.duckdns.org:5000/"
else
    echo "❌ Flask is not responding. Last log lines:"
    journalctl -u myportfolio -n 20 --no-pager
    exit 1
fi
