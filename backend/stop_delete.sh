#!/bin/bash

# Stop the delete service
if [ -f "delete_pid.txt" ]; then
    kill -9 $(cat delete_pid.txt)
    rm delete_pid.txt
    echo "delete service stopped."
else
    echo "delete service is not running."
fi
