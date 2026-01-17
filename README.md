# Neighborhood Library Service

A library management service built with **Django (DRF)** and **React**.

## Architecture

- **Backend**: Django REST Framework (Python 3)
- **Frontend**: React.js (Create React App)
- **Database**: PostgreSQL

## Project Structure

```
numino/
├── django_backend/       # Django Project (API)
│   ├── library/          # Library App (Models, Views, Services)
│   ├── numino/           # Project Settings
│   ├── requirements.txt  # Python dependencies
│   └── manage.py         # Django management script
├── frontend/             # React Application
│   ├── src/              # Source code
│   └── package.json      # Dependencies
├── schema.sql            # Database schema
├── setup.sh              # Setup script
└── start_services.sh     # Run script
```

## Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose (for PostgreSQL)

## Setup Instructions

### 1. Automated Setup (Recommended)

Run the setup script to initialize the database, backend, and frontend environments.

```bash
chmod +x setup.sh
./setup.sh
```

### 2. Manual Setup

#### Database
Start PostgreSQL:
```bash
docker-compose up -d
```
Initialize schema (if not using Django migrations for initial setup, though Django migrations are preferred now):
```bash
docker exec -i numino_postgres psql -U numino_user -d numino_db < schema.sql
```

#### Backend
```bash
cd django_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

#### Frontend
```bash
cd frontend
npm install
```

## Running the Application

Use the helper script to start both backend and frontend:

```bash
chmod +x start_services.sh
./start_services.sh
```

Or run them individually:

**Backend**: `http://localhost:8000`
```bash
cd django_backend
source venv/bin/activate
python manage.py runserver
```

**Frontend**: `http://localhost:3000`
```bash
cd frontend
npm start
```

## API Endpoints

The API is served at `http://localhost:8000/api/`.

### Books
- `GET /api/books/` - List all books
- `POST /api/books/` - Create a new book
- `GET /api/books/{id/` - Retrieve a book
- `POST /api/books/{id}/borrow/` - Borrow a book
- `POST /api/books/{id}/return/` - Return a book

### Members
- `GET /api/members/` - List all members
- `POST /api/members/` - Create a new member
- `GET /api/members/{id}/` - Retrieve a member
- `GET /api/members/{id}/borrowed-books/` - List books borrowed by member
