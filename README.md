# Neighborhood Library Service

A gRPC-based library management service built with Python, PostgreSQL, Node.js, and React.

## Architecture

- **Backend**: Python gRPC server with PostgreSQL
- **API Gateway**: Node.js Express server that bridges REST API calls to gRPC
- **Frontend**: React.js application with Bootstrap UI
- **Database**: PostgreSQL with transaction support and row-level locking

## Project Structure

```
numino/
├── backend/              # Python gRPC server
│   ├── proto/           # Protocol Buffer definitions
│   ├── server.py        # gRPC server implementation
│   ├── requirements.txt # Python dependencies
│   └── generate_proto.sh # Script to generate Python code from .proto
├── gateway/             # Node.js API Gateway
│   ├── server.js        # Express server with gRPC client
│   └── package.json     # Node.js dependencies
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/    # API service layer
│   └── package.json     # React dependencies
├── schema.sql           # Database schema
└── docker-compose.yml   # PostgreSQL container setup
```

## Prerequisites

- Python 3.11 or 3.12 (Python 3.13 is not yet fully supported by grpcio)
- Node.js 16+
- Docker and Docker Compose
- PostgreSQL client (optional, for direct DB access)

## Setup Instructions

### 1. Start PostgreSQL Database

```bash
docker-compose up -d
```

This will start PostgreSQL on port `5435` with:
- Database: `numino_db`
- User: `numino_user`
- Password: `numino_password`

### 2. Initialize Database Schema

```bash
# Connect to PostgreSQL and run the schema
psql -h localhost -p 5435 -U numino_user -d numino_db -f schema.sql

# Or using Docker
docker exec -i numino_postgres psql -U numino_user -d numino_db < schema.sql
```

### 3. Setup Python Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate gRPC Python code from proto files
chmod +x generate_proto.sh
./generate_proto.sh

# Create .env file (copy from .env.example if needed)
# DB_HOST=localhost
# DB_PORT=5435
# DB_NAME=numino_db
# DB_USER=numino_user
# DB_PASSWORD=numino_password

# Start the gRPC server
python server.py
```

The gRPC server will start on port `50051`.

### 4. Setup Node.js API Gateway

```bash
cd gateway

# Install dependencies
npm install

# Start the gateway server
npm start
```

The API Gateway will start on port `3001`.

### 5. Setup React Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start on port `3000` and open in your browser.

## API Endpoints

The API Gateway provides the following REST endpoints:

### Books
- `GET /api/books` - List all books
- `POST /api/books` - Create a new book
- `PUT /api/books/:id` - Update a book

### Members
- `POST /api/members` - Create a new member
- `PUT /api/members/:id` - Update a member

### Borrowing/Returning
- `POST /api/books/:bookId/borrow` - Borrow a book
- `POST /api/books/:bookId/return` - Return a book
- `GET /api/members/:memberId/borrowed-books` - List books borrowed by a member

## Frontend Features

The React frontend includes three main screens:

1. **Book List** (`/`) - Displays all books with their availability status
2. **Create Book** (`/create-book`) - Form to add new books to the library
3. **Borrow Book** (`/borrow-book`) - Interface to borrow available books

## Database Design

The database uses three main tables:

- **member**: Stores library member information
- **book**: Tracks books with current borrowing state (O(1) lookups)
- **ledger**: Transaction history for all borrow/return operations

The design uses both the `book` table for fast state queries and the `ledger` table for complete transaction history.

## Transaction and Locking

The service implements:
- **SERIALIZABLE isolation level** for borrow/return operations
- **Row-level locking** using `FOR UPDATE` to prevent concurrent modifications
- **Transaction rollback** on errors to maintain data consistency

## Testing the Service

### Using the Frontend

1. Navigate to `http://localhost:3000`
2. Click "Add Book" to create a new book
3. Use "Borrow Book" to borrow a book (you'll need a member ID)

### Using cURL

```bash
# Create a book
curl -X POST http://localhost:3001/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"}'

# List books
curl http://localhost:3001/api/books

# Create a member
curl -X POST http://localhost:3001/api/members \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Borrow a book (replace BOOK_ID and MEMBER_ID)
curl -X POST http://localhost:3001/api/books/1/borrow \
  -H "Content-Type: application/json" \
  -d '{"member_id": 1}'
```

## Troubleshooting

### gRPC Server Issues
- Ensure PostgreSQL is running: `docker-compose ps`
- Check database connection in `.env` file
- Verify proto files are generated: `ls backend/*_pb2*.py`

### API Gateway Issues
- Ensure gRPC server is running on port 50051
- Check that proto file path is correct in `gateway/server.js`

### Frontend Issues
- Ensure API Gateway is running on port 3001
- Check browser console for CORS or connection errors

## Development Notes

- The service implements minimum required functionality
- Database operations use transactions and locking to prevent race conditions
- Error handling is implemented for common scenarios (book already borrowed, member not found, etc.)
- The frontend uses Bootstrap for styling as per requirements

## License

This project is created for assignment purposes.

