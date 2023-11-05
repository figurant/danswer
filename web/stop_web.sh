#!/bin/bash

if [ -f "web_pid.txt" ]; then
    kill -9 $(cat web_pid.txt)
    rm web_pid.txt
    echo "Web service stopped."
else
    echo "Web service is not running."
fi
