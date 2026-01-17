import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { bookService, borrowService } from '../services/api';
import ConfirmationModal from './ConfirmationModal';

function Dashboard() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [returning, setReturning] = useState(null);
  const [bookToReturn, setBookToReturn] = useState(null);

  useEffect(() => {
    loadRecentBooks();
  }, []);

  const loadRecentBooks = async () => {
    try {
      setLoading(true);
      const response = await bookService.listRecentBooks(20);
      // Response now has consistent structure with books array
      setBooks(response.data.books || response.data || []);
      setError(null);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to load recent books';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleReturnClick = (book) => {
    if (!book.is_borrowed || !book.current_member) {
      return;
    }
    setBookToReturn(book);
  };

  const handleReturnConfirm = async () => {
    if (!bookToReturn) return;

    try {
      setReturning(bookToReturn.id);
      await borrowService.returnBook(bookToReturn.id, bookToReturn.current_member);
      toast.success(`"${bookToReturn.title}" returned successfully!`);
      setBookToReturn(null);
      await loadRecentBooks();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to return book');
    } finally {
      setReturning(null);
    }
  };

  const handleReturnCancel = () => {
    setBookToReturn(null);
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Recent Updates</h2>
        <button className="btn btn-primary" onClick={loadRecentBooks}>
          Refresh
        </button>
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
        <div className="row">
          {books.length === 0 ? (
            <div className="col-12">
              <div className="alert alert-info">No books found. Add some books to get started!</div>
            </div>
          ) : (
            books.map((book) => (
              <div key={book.id} className="col-md-6 col-lg-4 mb-4">
                <div className="card h-100">
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start">
                      <div className="flex-grow-1">
                        <h5 className="card-title">{book.title}</h5>
                        <p className="card-text">
                          <strong>Author:</strong> {book.author}
                        </p>
                        <p className="card-text">
                          <span className={`badge ${book.is_borrowed ? 'bg-danger' : 'bg-success'}`}>
                            {book.is_borrowed ? 'Borrowed' : 'Available'}
                          </span>
                        </p>
                        {book.is_borrowed && book.current_member_name && (
                          <p className="card-text text-muted small">
                            <strong>Borrowed by:</strong> {book.current_member_name}
                          </p>
                        )}
                      </div>
                      {book.is_borrowed && (
                        <div className="dropdown">
                          <button
                            className="btn btn-sm btn-outline-secondary"
                            type="button"
                            id={`dropdown-${book.id}`}
                            data-bs-toggle="dropdown"
                            aria-expanded="false"
                            disabled={returning === book.id}
                          >
                            {returning === book.id ? (
                              <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                            ) : (
                              '⋮'
                            )}
                          </button>
                          <ul className="dropdown-menu" aria-labelledby={`dropdown-${book.id}`}>
                            <li>
                              <button
                                className="dropdown-item"
                                onClick={() => handleReturnClick(book)}
                                disabled={returning === book.id}
                              >
                                Return Book
                              </button>
                            </li>
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <ConfirmationModal
        show={!!bookToReturn}
        onConfirm={handleReturnConfirm}
        onCancel={handleReturnCancel}
        title="Return Book"
        message={bookToReturn ? `Are you sure you want to return "${bookToReturn.title}"?` : ''}
        confirmText="Return"
        cancelText="Cancel"
        confirmVariant="primary"
        isProcessing={returning === bookToReturn?.id}
      />
    </div>
  );
}

export default Dashboard;

