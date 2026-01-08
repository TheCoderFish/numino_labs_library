# Backend Architecture Refactoring

## Overview

The backend has been refactored to follow a clean architecture pattern with proper separation of concerns. The new structure introduces Repository and Service layers to improve testability, reusability, and maintainability.

## Previous Architecture

```
gRPC Handlers (server.py)
    ↓
Database Helper (db_helper.py)
```

**Issues:**
- Tight coupling between gRPC layer and database operations
- Business logic mixed with data access
- Difficult to test business logic independently
- Poor reusability of components

## New Architecture

```
gRPC Handlers (server.py)
    ↓
Service Layer (services/)
    ↓
Repository Layer (repositories/)
    ↓
Database Models (db_helper.py)
```

## Layer Responsibilities

### 1. Repository Layer (`repositories/`)
Handles all database operations and data access logic.

- **BaseRepository**: Common database session management
- **BookRepository**: Book-specific database operations
- **MemberRepository**: Member-specific database operations
- **LedgerRepository**: Transaction logging operations

**Benefits:**
- Single responsibility: Only data access
- Easy to mock for testing
- Can be reused across different services
- Database logic is isolated

### 2. Service Layer (`services/`)
Contains business logic and orchestrates operations across repositories.

- **BaseService**: Common validation logic
- **BookService**: Book business operations (CRUD, validation)
- **MemberService**: Member business operations (CRUD, validation)
- **LibraryService**: Library operations (borrow/return books)

**Benefits:**
- Business rules are centralized
- Easy to test business logic
- Services can be reused by different handlers
- Clear separation of concerns

### 3. Handler Layer (`server.py`)
Handles gRPC-specific concerns and delegates to services.

- **LibraryService**: gRPC service implementation
- Focuses on protocol buffer conversion
- Error handling and logging
- HTTP/gRPC specific logic

**Benefits:**
- Thin controllers focused on protocol concerns
- Easy to change protocols (REST, GraphQL, etc.)
- Service logic can be reused

## Key Improvements

### 1. Testability
- **Unit Tests**: Services and repositories can be tested in isolation
- **Mocking**: Dependencies can be easily mocked
- **Integration Tests**: Still available at the handler level

### 2. Reusability
- Services can be used by different handlers (gRPC, REST, GraphQL)
- Repositories can be shared across services
- Business logic is decoupled from presentation layer

### 3. Separation of Concerns
- Data access is separate from business logic
- Business logic is separate from presentation
- Each layer has a single responsibility

### 4. Maintainability
- Changes to database don't affect business logic
- Changes to business logic don't affect handlers
- Easier to modify and extend functionality

## Example: Creating a Book

### Before:
```python
# server.py
def CreateBook(self, request, context):
    Book.validate_data(request.title, request.author)
    result = DatabaseHelper.create_book(request.title, request.author)
    # ... protobuf conversion
```

### After:
```python
# server.py
def CreateBook(self, request, context):
    result = self._book_service.create_book(request.title, request.author)
    # ... protobuf conversion

# services/book_service.py
def create_book(self, title: str, author: str) -> Dict[str, Any]:
    self.validate_book_data(title, author)
    return self._book_repository.create_book(title, author)

# repositories/book_repository.py
def create_book(self, title: str, author: str) -> Dict[str, Any]:
    # ... database operations
```

## Testing Strategy

### Unit Tests (`tests/test_services.py`)
- Test services with mocked repositories
- Test business logic in isolation
- Fast and focused tests

### Integration Tests (`tests/test_books.py`, etc.)
- Test full request/response cycle
- Test gRPC handlers with real database
- Ensure end-to-end functionality

## Migration Notes

- Existing gRPC API remains unchanged
- Database schema unchanged
- All existing functionality preserved
- Tests need to be updated to work with new structure
- New unit tests added for better coverage

## Future Benefits

- Easy to add REST API alongside gRPC
- Simple to switch databases (repository interface remains same)
- Business logic can be reused in different contexts
- Better error handling and logging
- Improved code organization and readability