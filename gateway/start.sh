#!/bin/bash

# Gateway start script
# Kills any process on port 3001 and starts the gateway server

PORT=3001

echo "Starting API Gateway..."

# Find and kill any process using the port
PID=$(lsof -ti :$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "Port $PORT is in use by process $PID. Killing it..."
    kill -9 $PID 2>/dev/null
    sleep 1
    echo "Port $PORT is now free."
fi

# Start the server
echo "Starting gateway server on port $PORT..."
node server.js

