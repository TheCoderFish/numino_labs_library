#!/bin/bash

echo "Starting Neighborhood Library Services..."
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill 0
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start Backend (gRPC)
echo "1. Starting Backend (gRPC)..."
cd backend
source venv/bin/activate
python server.py &
BACKEND_PID=$!
cd ..
echo "   ✓ Backend started (PID: $BACKEND_PID)"

# Start Gateway (Node.js)
echo "2. Starting Gateway (Node.js)..."
cd gateway
npm start &
GATEWAY_PID=$!
cd ..
echo "   ✓ Gateway started (PID: $GATEWAY_PID)"

# Start Frontend (React)
echo "3. Starting Frontend (React)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..
echo "   ✓ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "All services started! 🎉"
echo ""
echo "  - Backend (gRPC):    http://localhost:50051"
echo "  - Gateway (API):     http://localhost:3001"
echo "  - Frontend (React):  http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait