#!/bin/bash

# Stop the backend service
if [ -f "backend_pid.txt" ]; then
    kill -9 $(cat backend_pid.txt)
    rm backend_pid.txt
    echo "Backend service stopped."
else
    echo "Backend service is not running."
fi
