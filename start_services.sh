#!/bin/bash

echo "Starting Neighborhood Library Services (Django + React)..."
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

# Start Django Backend
echo "1. Starting Backend (Django)..."
cd django_backend
source venv/bin/activate
python manage.py runserver 8000 &
BACKEND_PID=$!
cd ..
echo "   ✓ Django Backend started (PID: $BACKEND_PID)"

# Start Frontend (React)
echo "2. Starting Frontend (React)..."
cd frontend
# Ensure frontend knows about the new API port
export REACT_APP_API_URL=http://localhost:8000/api
npm start &
FRONTEND_PID=$!
cd ..
echo "   ✓ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "All services started! 🎉"
echo ""
echo "  - Backend (Django):  http://localhost:8000"
echo "  - Frontend (React):  http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait