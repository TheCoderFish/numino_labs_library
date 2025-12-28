#!/bin/bash

# Generate Python code from proto files
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/library.proto

echo "Proto files generated successfully!"

