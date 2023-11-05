#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR"/../../.venv/bin/activate

# Check if the backend service is already running
if [ -f "$SCRIPT_DIR/backend_pid.txt" ]; then
    echo "Backend service is already running."
    exit 0
fi

# Set environment variables
export DYNAMIC_CONFIG_DIR_PATH="$SCRIPT_DIR/dynamic_config_storage"
export GEN_AI_API_KEY=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
export VESPA_DEPLOYMENT_ZIP="$SCRIPT_DIR/danswer/datastores/vespa/vespa-app.zip"
export FILE_CONNECTOR_TMP_STORAGE_PATH="$SCRIPT_DIR/danwser_file_storage"
export WEB_DOMAIN="http://hk3.dev.selectdb-in.cc:3088"
export OAUTH_TYPE=google
export GOOGLE_OAUTH_CLIENT_ID=4508245975-elvpqor8jl83imdvuap0oh2u3d3l4ab4.apps.googleusercontent.com
export GOOGLE_OAUTH_CLIENT_SECRET=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
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST="10.16.10.6"
export POSTGRES_PORT=25432
export POSTGRES_db=postgres

# Navigate to the directory
cd "$SCRIPT_DIR"

# Run the backend with uvicorn
nohup uvicorn danswer.main:app --reload --port 8080 > logs/backend.log 2>&1 &
echo $! >backend_pid.txt
echo "Backend service started."
