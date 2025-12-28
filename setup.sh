#!/bin/bash

echo "Setting up Neighborhood Library Service..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start PostgreSQL
echo "1. Starting PostgreSQL database..."
docker-compose up -d
sleep 5

# Initialize database schema
echo "2. Initializing database schema..."
docker exec -i numino_postgres psql -U numino_user -d numino_db < schema.sql
if [ $? -eq 0 ]; then
    echo "   ✓ Database schema initialized"
else
    echo "   ✗ Failed to initialize schema"
    exit 1
fi

# Setup Python backend
echo "3. Setting up Python backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
chmod +x generate_proto.sh
./generate_proto.sh
cd ..
echo "   ✓ Python backend ready"

# Setup Node.js gateway
echo "4. Setting up Node.js API Gateway..."
cd gateway
npm install > /dev/null 2>&1
cd ..
echo "   ✓ API Gateway ready"

# Setup React frontend
echo "5. Setting up React frontend..."
cd frontend
npm install > /dev/null 2>&1
cd ..
echo "   ✓ React frontend ready"

echo ""
echo "Setup complete! 🎉"
echo ""
echo "To start the services:"
echo "  1. Backend (gRPC):    cd backend && source venv/bin/activate && python server.py"
echo "  2. Gateway (Node.js): cd gateway && npm start"
echo "  3. Frontend (React):  cd frontend && npm start"
echo ""
echo "Note: Make sure to create a .env file in the backend directory with database credentials."

