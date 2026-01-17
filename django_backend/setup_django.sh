#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Numino Django Backend Setup...${NC}"

# 1. Start Database
echo -e "${BLUE}[1/5] Starting PostgreSQL with Docker...${NC}"
cd .. && docker-compose up -d && cd django_backend
# Wait for DB to be ready script or sleep?
echo "Waiting for Database to initialize..."
sleep 3

# 2. Check/Create Virtual Environment
echo -e "${BLUE}[2/5] Setting up Python Virtual Environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
fi
source venv/bin/activate

# 3. Install Dependencies
echo -e "${BLUE}[3/5] Installing Dependencies...${NC}"
pip install -r requirements.txt

# 4. Migrate Database
echo -e "${BLUE}[4/5] Running Database Migrations...${NC}"
# We might want to ensure a clean slate if requested, but standard migrate is safer
python manage.py migrate

# 5. Run Tests
echo -e "${BLUE}[5/5] Running Unit Tests...${NC}"
pytest

# 6. Start Server
echo -e "${GREEN}Setup Complete! Starting Server on port 8000...${NC}"
python manage.py runserver 8000
