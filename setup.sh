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

# Setup Django backend
echo "2. Setting up Django backend..."
cd django_backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "   Running migrations..."
python manage.py migrate > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Database schema initialized (via Django migrations)"
else
    echo "   ✗ Failed to run migrations"
    exit 1
fi
cd ..
echo "   ✓ Django backend ready"

# Setup React frontend
echo "3. Setting up React frontend..."
cd frontend
npm install > /dev/null 2>&1
cd ..
echo "   ✓ React frontend ready"

echo ""
echo "Setup complete! 🎉"
echo ""
echo "To start the services, run:"
echo "  ./start_services.sh"
echo ""
