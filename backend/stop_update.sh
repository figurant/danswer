#!/bin/bash

# Stop the update service
if [ -f "update_pid.txt" ]; then
    kill -9 $(cat update_pid.txt)
    rm update_pid.txt
    echo "update service stopped."
else
    echo "update service is not running."
fi
