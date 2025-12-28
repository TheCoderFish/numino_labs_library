#!/bin/bash

cd "$(dirname "$0")"
source venv/bin/activate

# Make sure proto files are generated
./generate_proto.sh

# Start the server
python server.py

