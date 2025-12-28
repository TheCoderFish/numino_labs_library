# Backend Tests

This directory contains pytest tests for the Library Management System backend.

## Running Tests

To run the tests:

```bash
cd backend
source venv/bin/activate
python -m pytest tests/
```

## Test Coverage

### Books (`test_books.py`)
- ✅ Create book successfully
- ✅ Update book successfully
- ✅ Update non-existent book (error handling)
- ✅ List all books
- ✅ Search books by title/author

### Members (`test_members.py`)
- ✅ Create member successfully
- ✅ Create member with duplicate email (error handling)
- ✅ Update member successfully
- ✅ Update non-existent member (error handling)
- ✅ Update member to duplicate email (error handling)
- ✅ List all members
- ✅ Search members by name/email

### Ledger (`test_ledger.py`)
- ✅ Borrow book successfully
- ✅ Borrow non-existent book (error handling)
- ✅ Borrow with non-existent member (error handling)
- ✅ Borrow already borrowed book (error handling)
- ✅ Double borrow by same member (error handling)
- ✅ Return book successfully
- ✅ Return unborrowed book (error handling)
- ✅ Return book by wrong member (error handling)
- ✅ Double return (error handling)
- ✅ List borrowed books for member

## Database Transactions and Locking

The ledger operations use PostgreSQL's SERIALIZABLE isolation level and row-level locking to prevent race conditions:

- Double borrowing prevention
- Concurrent borrow/return protection
- Data consistency guarantees

## Validation

- Basic input validation in the Node.js gateway
- Database constraint validation in the Python backend
- Proper error propagation to clients