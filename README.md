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

## Pagination

The API uses **cursor-based pagination** for efficient data retrieval. All list endpoints (Books, Members) support pagination.

### How It Works

Cursor pagination provides stable pagination even when data is being added or removed. It uses an opaque cursor string to track position.

**Response Format:**
```json
{
  "next": "http://localhost:8000/api/books/?cursor=bz01&page_size=20",
  "previous": "http://localhost:8000/api/books/?cursor=cj0x...",
  "results": [...]
}
```

### Parameters

- `page_size` - Number of items per page (default: 20, max: 100)
- `cursor` - Opaque cursor string for navigation (provided in `next`/`previous`)

### Examples

```bash
# Get first page of books (20 items)
curl http://localhost:8000/api/books/

# Get first 10 books
curl http://localhost:8000/api/books/?page_size=10

# Navigate to next page using cursor from response
curl "http://localhost:8000/api/books/?cursor=bz01&page_size=10"

# Get members with pagination
curl http://localhost:8000/api/members/?page_size=15
```

### Ordering

- **Books**: Ordered by `updated_at` (descending) - most recently updated first
- **Members**: Ordered by `id` (ascending)
