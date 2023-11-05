#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

# Check if the backend service is already running
if [ -f "$SCRIPT_DIR/web_pid.txt" ]; then
    echo "Web service is already running."
    exit 0
fi

# Navigate to the directory
cd "$SCRIPT_DIR"

# Run the backend with uvicorn
nohup npm run dev -- --port 3088 > web.log 2>&1 &
echo $! >web_pid.txt
echo "Web service started."
