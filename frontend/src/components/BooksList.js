import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { bookService, borrowService } from '../services/api';

function BooksList() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [returning, setReturning] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [nextCursor, setNextCursor] = useState(null);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  useEffect(() => {
    loadBooks(true);
  }, [searchQuery, filter]);

  const loadBooks = async (reset = false) => {
    try {
      if (reset) {
        setLoading(true);
        setBooks([]);
        setNextCursor(null);
      } else {
        setLoadingMore(true);
      }
      
      const params = {
        limit: 20,
        search: searchQuery,
        filter: filter
      };
      
      if (!reset && nextCursor) {
        params.cursor = nextCursor;
      }
      
      const response = await bookService.listBooks(params);
      const newBooks = reset ? response.data.books : [...books, ...response.data.books];
      
      setBooks(newBooks);
      setNextCursor(response.data.next_cursor || null);
      setHasMore(response.data.has_more);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load books');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleReturn = async (book) => {
    if (!book.is_borrowed || !book.current_member_id) {
      return;
    }

    if (!window.confirm(`Return "${book.title}"?`)) {
      return;
    }

    try {
      setReturning(book.id);
      await borrowService.returnBook(book.id, book.current_member_id);
      // Reload books to reflect changes
      loadBooks(true);
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to return book');
    } finally {
      setReturning(null);
    }
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleFilterChange = (e) => {
    setFilter(e.target.value);
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Books</h2>
        <div>
          <Link to="/create-book" className="btn btn-primary me-2">
            Add Book
          </Link>
          <button className="btn btn-outline-secondary" onClick={() => loadBooks(true)}>
            Refresh
          </button>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="row mb-3">
        <div className="col-md-6">
          <input
            type="text"
            className="form-control"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>
        <div className="col-md-3">
          <select
            className="form-select"
            value={filter}
            onChange={handleFilterChange}
          >
            <option value="all">All Books</option>
            <option value="available">Available</option>
            <option value="borrowed">Borrowed</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Status</th>
                <th>Borrowed By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {books.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center">
                    <div className="alert alert-info mb-0">No books found. Add some books to get started!</div>
                  </td>
                </tr>
              ) : (
                books.map((book) => (
                  <tr key={book.id}>
                    <td>{book.id}</td>
                    <td>{book.title}</td>
                    <td>{book.author}</td>
                    <td>
                      <span className={`badge ${book.is_borrowed ? 'bg-danger' : 'bg-success'}`}>
                        {book.is_borrowed ? 'Borrowed' : 'Available'}
                      </span>
                    </td>
                    <td>{book.current_member_name || '-'}</td>
                    <td>
                      {book.is_borrowed ? (
                        <button
                          className="btn btn-sm btn-outline-primary"
                          onClick={() => handleReturn(book)}
                          disabled={returning === book.id}
                        >
                          {returning === book.id ? (
                            <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                          ) : (
                            'Return'
                          )}
                        </button>
                      ) : (
                        <span className="text-muted">-</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
          
          {hasMore && (
            <div className="text-center mt-3">
              <button
                className="btn btn-outline-primary"
                onClick={() => loadBooks(false)}
                disabled={loadingMore}
              >
                {loadingMore ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Loading...
                  </>
                ) : (
                  'Load More'
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default BooksList;

