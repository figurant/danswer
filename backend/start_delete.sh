#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR"/../../.venv/bin/activate

# Check if the delete service is already running
if [ -f "$SCRIPT_DIR/delete_pid.txt" ]; then
    echo "delete service is already running."
    exit 0
fi

# Set environment variables
export DYNAMIC_CONFIG_DIR_PATH="$SCRIPT_DIR/dynamic_config_storage"
export GEN_AI_API_KEY=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
export VESPA_DEPLOYMENT_ZIP="$SCRIPT_DIR/danswer/datastores/vespa/vespa-app.zip"
export FILE_CONNECTOR_TMP_STORAGE_PATH="$SCRIPT_DIR/danwser_file_storage"
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST="10.16.10.6"
export POSTGRES_PORT=25432
export POSTGRES_db=postgres
export LOG_FILE_STORAGE=$SCRIPT_DIR/logs/background
export PYTHONPATH=$SCRIPT_DIR
# Navigate to the directory
cd "$SCRIPT_DIR"

# Run the delete with uvicorn
nohup python danswer/background/connector_deletion.py > logs/delete.log 2>&1 &
echo $! >delete_pid.txt
echo "delete service started."
