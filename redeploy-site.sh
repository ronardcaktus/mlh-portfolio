#!/bin/bash

set -e

# 1. cd into project folder
# Default to the directory where this script lives so it works from any cwd.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
echo "Navigating to project directory..."
cd "$PROJECT_DIR" || { echo "Error: Could not enter directory $PROJECT_DIR"; exit 1; }

# 2. Fetch latest changes and hard reset to origin/main
echo "Updating code from GitHub main branch..."
git fetch && git reset --hard origin/main

# 3. Stop containers before rebuild to reduce memory pressure on VPS
echo "Stopping existing containers..."
docker compose -f docker-compose.prod.yml down

# 4. Build and start updated containers
echo "Building and starting containers..."
docker compose -f docker-compose.prod.yml up -d --build

echo "App deployed"
echo "http://rmoon.duckdns.org:5001/"
