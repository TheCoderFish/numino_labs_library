import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { bookService, borrowService } from '../services/api';

function BooksList() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [returning, setReturning] = useState(null);

  useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const response = await bookService.listBooks();
      setBooks(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load books');
    } finally {
      setLoading(false);
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
      await loadBooks();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to return book');
    } finally {
      setReturning(null);
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Books</h2>
        <div>
          <Link to="/create-book" className="btn btn-primary">
            Add Book
          </Link>
          <button className="btn btn-outline-secondary ms-2" onClick={loadBooks}>
            Refresh
          </button>
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
        </div>
      )}
    </div>
  );
}

export default BooksList;

